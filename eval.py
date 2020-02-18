import argparse
import pprint
from typing import Dict

from yacs.config import CfgNode
import yaml

from baselines.agents import *  # specific agent is given in agent-config
from tesse_gym import NetworkConfig
from tesse_gym.eval.agent import Agent
from tesse_gym.eval.goseek_benchmark import GoSeekBenchmark
from tesse_gym.eval.utils import get_agent_cls

from config.config import get_cfg_defaults


def main(
    episode_args: CfgNode, agent_args: Dict[str, Any]
) -> Dict[str, Dict[str, float]]:
    """ Run GOSEEK evaluation over the specified environment and
    agent configurations.

    Args:
        episode_args (CfgNode): Environment configurations.
        agent_args (Dict[str, Any]): Agent configurations.

    Returns:
        Dict[str, Dict[str, float]]: Dictionary containing overall evaluation performance as
            well as a summary for each episode.
    """
    benchmark = GoSeekBenchmark(
        build_path=episode_args.ENV.sim_path,
        scenes=episode_args.EPISODE.scenes,
        episode_length=episode_args.EPISODE.episode_length,
        n_targets=episode_args.EPISODE.n_targets,
        success_dist=episode_args.EPISODE.success_dist,
        random_seeds=episode_args.EPISODE.random_seeds,
        network_config=NetworkConfig(
            position_port=episode_args.ENV.position_port,
            image_port=episode_args.ENV.image_port,
            metadata_port=episode_args.ENV.metadata_port,
            step_port=episode_args.ENV.step_port
        ),
        ground_truth_mode=episode_args.ENV.ground_truth_mode,
    )
    agent = get_agent_cls(agent_args["name"], Agent)(agent_args)
    return benchmark.evaluate(agent)


if __name__ == "__main__":
    episode_cfg = get_cfg_defaults()

    parser = argparse.ArgumentParser()
    parser.add_argument("--episode-config", type=str)
    parser.add_argument("--agent-config", type=str)
    args = parser.parse_args()

    with open(args.agent_config) as f:
        agent_args = yaml.load(f, Loader=yaml.FullLoader)

    if args.episode_config:
        episode_cfg.merge_from_file(args.episode_config)

    episode_cfg.freeze()

    results = main(episode_cfg, agent_args)

    print("------ Environment Configuration -----")
    pprint.pprint(episode_cfg, depth=5)

    print("\n----- Agent Configuration -----")
    pprint.pprint(agent_args, depth=5)

    print("\n----- Per Episode Score -----")
    pprint.pprint(results, depth=5)
