"""Frozen visual encoders for the taskcraft observation-pipeline comparison.

Wraps VPT, R3M, VIP, and CLIP behind one interface so a downstream policy
head can be trained on top of any of them without changing the training
code. All encoders are frozen (eval mode, no_grad, requires_grad=False) per
CLAUDE.md's VRAM constraint (encoder freeze + policy head only).
"""

import os
import sys

import numpy as np
import torch
from PIL import Image
from torchvision import transforms as T

THIRD_PARTY = r"C:\KoreaUniv\projects\taskcraft\third_party"


class FrozenEncoder:
    """Common interface: raw MineRL POV frames in, a feature tensor out."""

    name: str
    feature_dim: int

    def encode(self, frames: np.ndarray) -> torch.Tensor:
        """frames: (N, H, W, 3) uint8 RGB. Returns (N, feature_dim) float tensor on self.device."""
        raise NotImplementedError


class VPTEncoder(FrozenEncoder):
    """Wraps VPT's MinecraftPolicy trunk directly, bypassing the action/value
    heads. Each frame is encoded independently with a freshly reset hidden
    state, so this does not use VPT's temporal/recurrent context -- only its
    visual representation is being compared here.
    """

    name = "vpt"

    def __init__(self, model_path=None, weights_path=None, device="cuda"):
        if THIRD_PARTY not in sys.path:
            sys.path.insert(0, os.path.join(THIRD_PARTY, "vpt"))

        import pickle
        from minerl.herobraine.env_specs.human_survival_specs import HumanSurvival
        from agent import MineRLAgent, ENV_KWARGS, resize_image, AGENT_RESOLUTION

        model_path = model_path or os.path.join(THIRD_PARTY, "vpt", "models", "foundation-model-1x.model")
        weights_path = weights_path or os.path.join(THIRD_PARTY, "vpt", "models", "foundation-model-1x.weights")

        env = HumanSurvival(**ENV_KWARGS).make()
        agent_parameters = pickle.load(open(model_path, "rb"))
        policy_kwargs = agent_parameters["model"]["args"]["net"]["args"]
        pi_head_kwargs = agent_parameters["model"]["args"]["pi_head_opts"]
        pi_head_kwargs["temperature"] = float(pi_head_kwargs["temperature"])

        self._agent = MineRLAgent(env, device=device, policy_kwargs=policy_kwargs, pi_head_kwargs=pi_head_kwargs)
        self._agent.load_weights(weights_path)
        self._resize_image = resize_image
        self._agent_resolution = AGENT_RESOLUTION

        self.device = torch.device(device)
        self.feature_dim = policy_kwargs["hidsize"]

        for p in self._agent.policy.parameters():
            p.requires_grad_(False)
        self._agent.policy.eval()

    @torch.no_grad()
    def encode(self, frames: np.ndarray) -> torch.Tensor:
        feats = []
        for frame in frames:
            self._agent.reset()
            # net expects (batch, time, H, W, C); we feed one frame as a
            # length-1 sequence, same as MinecraftAgentPolicy.act() does via
            # tree_map(lambda x: x.unsqueeze(1), obs) before calling self.net.
            img = self._resize_image(frame, self._agent_resolution)[None, None]
            agent_input = {"img": torch.from_numpy(img).to(self.device)}
            first = self._agent._dummy_first.unsqueeze(1)
            (pi_h, _), _ = self._agent.policy.net(
                agent_input,
                self._agent.hidden_state,
                context={"first": first},
            )
            feats.append(pi_h.reshape(-1))
        return torch.stack(feats)


class _TorchvisionEncoder(FrozenEncoder):
    """Shared plumbing for the ImageNet-style encoders (R3M, VIP): resize to
    224x224, run through a frozen resnet, return the pooled feature.
    """

    def __init__(self, model, feature_dim, device="cuda"):
        self._model = model.to(device).eval()
        for p in self._model.parameters():
            p.requires_grad_(False)
        self.device = torch.device(device)
        self.feature_dim = feature_dim
        self._transform = T.Compose([T.Resize((224, 224)), T.ToTensor()])

    @torch.no_grad()
    def encode(self, frames: np.ndarray) -> torch.Tensor:
        batch = torch.stack([self._transform(Image.fromarray(f)) for f in frames])
        batch = (batch * 255.0).to(self.device)  # R3M/VIP expect 0-255, not ImageNet-normalized
        return self._model(batch)


class R3MEncoder(_TorchvisionEncoder):
    name = "r3m"

    def __init__(self, device="cuda"):
        if os.path.join(THIRD_PARTY, "r3m") not in sys.path:
            sys.path.insert(0, os.path.join(THIRD_PARTY, "r3m"))
        from r3m import load_r3m

        super().__init__(load_r3m("resnet50"), feature_dim=2048, device=device)


class VIPEncoder(_TorchvisionEncoder):
    name = "vip"

    def __init__(self, device="cuda"):
        if os.path.join(THIRD_PARTY, "vip") not in sys.path:
            sys.path.insert(0, os.path.join(THIRD_PARTY, "vip"))
        from vip import load_vip

        super().__init__(load_vip(), feature_dim=1024, device=device)


class CLIPEncoder(FrozenEncoder):
    """Generic vision encoder, not trained for any embodiment-agnostic
    objective. Serves as the control: if R3M/VIP don't beat this, their
    training objective isn't adding anything over a generic visual encoder.
    """

    name = "clip"

    def __init__(self, device="cuda"):
        import open_clip

        # NOTE: must use the "-quickgelu" variant with the "openai" pretrained
        # tag, or the activation function doesn't match what the weights were
        # trained with (open_clip warns about this otherwise).
        model, _, preprocess = open_clip.create_model_and_transforms(
            "ViT-B-32-quickgelu", pretrained="openai"
        )
        self._model = model.to(device).eval()
        for p in self._model.parameters():
            p.requires_grad_(False)
        self._preprocess = preprocess
        self.device = torch.device(device)
        self.feature_dim = 512

    @torch.no_grad()
    def encode(self, frames: np.ndarray) -> torch.Tensor:
        batch = torch.stack([self._preprocess(Image.fromarray(f)) for f in frames]).to(self.device)
        return self._model.encode_image(batch)


_REGISTRY = {
    "vpt": VPTEncoder,
    "r3m": R3MEncoder,
    "vip": VIPEncoder,
    "clip": CLIPEncoder,
}


def get_encoder(name: str, device: str = "cuda") -> FrozenEncoder:
    if name not in _REGISTRY:
        raise ValueError(f"Unknown encoder '{name}', expected one of {list(_REGISTRY)}")
    return _REGISTRY[name](device=device)
