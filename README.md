<p align="center">
  <a href="https://quatern.co"><img src="https://quatern.co/docs/assets/favicon.svg" alt="Quatern" width="96"></a>
</p>

# Quatern examples

[![examples](https://github.com/quatern-labs/quatern-examples/actions/workflows/examples.yml/badge.svg)](https://github.com/quatern-labs/quatern-examples/actions/workflows/examples.yml)

Examples of robot code written and verified with [Quatern](https://quatern.co).

## Usage

```sh
pipx install quatern
quatern
```

The first time, `quatern` offers to sign you in. You can sign in with GitHub
for free monthly usage of the hosted agent, paste your own Anthropic API key,
or skip. Most examples here need neither, and the ones that use the agent are
marked.

Then run any example. Each one is a short command sequence with its own
README:

```sh
quatern quickstart --robot turtlebot3_burger --world room --yes
```

Every example also has a `run.sh` that runs exactly what its README shows. To
keep your own `~/.quatern` untouched while you explore, give it a scratch
directory first: `export QUATERN_DATA_DIR=$(mktemp -d)`.

## A guided tour

| | Folder | What you'll learn | Needs |
| --- | --- | --- | --- |
| 1 | [`01_getting_started`](01_getting_started/) | The 2-minute simulator tour, and your first request to the agent | Nothing · agent example needs sign-in |
| 2 | [`02_your_robot`](02_your_robot/) | Set up your own robot from a URDF with `/init`, check it with `doctor`, or pick one from the catalog | Nothing |
| 3 | [`03_verification`](03_verification/) | Record a simulated capture, verify against it, what READY means, and how a cross-check catches a drifting sensor | Nothing |
| 4 | [`04_safety`](04_safety/) | The deploy gate, the watchdog stopping a run when you inject a fault, and reading an ABORTED run record | Nothing |
| 5 | [`05_navigation`](05_navigation/) | Hallway and room worlds: plan, deploy, keep drift in bounds | Nothing |
| 6 | [`06_perception`](06_perception/) | "Stop for obstacles using the lidar", asked of the agent | Sign-in (free) or an Anthropic key |
| | [`misc`](misc/) | Anything that doesn't fit the tour yet | |

**Needs** is one of:

- **Nothing**: runs entirely on your machine, in Quatern's built-in simulator.
  No key, no account, no ROS.
- **Sign-in (free) or an Anthropic key**: uses the agent. Run `quatern login`
  for free monthly usage on Quatern's hosted API, or set `ANTHROPIC_API_KEY`
  to use your own key.

Everything here runs in simulation. Moving a real robot is covered by
`quatern hardware --robot <name>` and the
[setup docs](https://quatern.co/docs/setup/#from-the-simulator-to-the-real-robot).

These examples are continuously tested against the latest Quatern release on
Python 3.11.

## Contributing

See [AGENTS.md](AGENTS.md) for how to run, add and test an example. If an
example is broken, [open an issue](https://github.com/quatern-labs/quatern-examples/issues/new?template=example-is-broken.yml).

## License

[MIT](LICENSE)
