# PROGNOSIS
### Black-Box Analysis of Network Protocol Implementations

```
implementations -> Different implementations to be learned.
adapters -> Protocol adapters for alphabet translation.
learner -> Java based abstract learner.
```

## Getting Started
#### 0. Prerequisites
Make sure you have Docker installed in your machine, and an internet connection to fetch/build the required Docker images.
The source for all images is provided, however you may prefer using the pre-built Docker images for heavy implementations.

This tool has been tested with Docker 20.10.5.
Apple Silicon / ARM support is provided on a best effort basis, if you'd like to run on ARM with emulation, be sure to add `platform: linux/amd64` to every service in `docker-compose.yaml`.

Make sure all git modules are initiated:
```bash
git submodule init
git submodule update
```

If you would like to repoduce results from the paper, please download them from [this link](https://drive.google.com/drive/folders/1ndo5-Ef7sznxx6xirThF1Exqq9BCZlEE), as they are too big to be held by Git.

#### 1. Target protocol and implementation
The various components work together through Docker Compose. By switching the image tag of the implementation container in `docker-compose.yaml`, we can work on different protocols and implementations.
Available protocol adapters: `quic`, `tcp`.
Available implementation tags: `quiche`, `msquic`, `proxygen`, `googlequic`, `tcp`.

#### 2. Learning parameters (config.yaml)
After that we can fine tune the learning process further. The setting for which are grouped in the root `config.yaml` file. Its syntax is as follows:
```yaml
learner:
    runsPerQuery: 3 # Minimmum number of runs per query (non-determinism detection).
    confidence: 85 # Required confidence in query answer for it to be used.
    maxAttempts: 100 # Max attempts per query, after which to declare the system non-det. and terminate.
    sutPort: 3333 # Port used to communicate with the adapter.
    sutIP: adapter # Adapter IP/DNS name.
    inputAlphabet: # List of symbols to learn a model over.
        - SYN(?,?,0)
        - SYN+ACK(?,?,0)
        - ACK(?,?,0)
adapter:
    adapter:
    adapterAddress: 0.0.0.0:3333 # socket to listen on.
    sulAddress: implementation:4433 # Implementation address.
    sulName: quic.tiferrei.com # Implementation name (used by QUIC)
    http3: true # Use HTTP3 (instead of HTTP2).
    tracing: false # Use debug tracing in output.
    waitTime: 400ms # Period of time to wait for a response from SUL.
    httpPath: / # HTTP base request path to query.
synthesizer:
    op1: 0
```

You will find the appropriate `config.yaml` settings for each model learned in their respective folder in `results`.

#### 3. Learn
We can now start the fully automated learning process with:
```
docker-compose up --remove-orphans learner
```

#### 4. (Optional) Synthesize
**⚠️  WARNING:** Synthesising rich models can be a memory intensive operations. Ensure Docker runs with at least 8GB of memory, 12GB recommended. 

```
docker-compose up --remove-orphans synthesizer
```

Do note that the synthesis process purposefuly does not terminate, and is in constant iteration. You will see the iterations starting to be written to `output/synth`, and the process can be stopped at any satisfactory time.

#### Extra - Running the analysis

```
docker build -t analysis .
docker run analysis
```


#### Counting traces

`Synthesis/det.py` will display the number of traces required for some depth before and after learning.

### FAQ

#### The learner did not terminate!

This can happen for a variety of reasons. Some are:

##### 1. Non-determinism in oracle query.
This issue is caught by the error: `SEVERE: Non-determinism found by probablistic oracle for input`.
This can be caused by several things. The most common is that the implementation being learned is not very stable, and after many queries will get into a non-deterministic state. If this is the case, simply restarting the process (with a fresh implementation container) will solve the issue. Previous queries are cached, so no progress is lost.

If this does not solve the issue then it might be that the waitTime needs to be increased to allow for packets arriving at inconsitent times.

If this still does not solve the issue, the query might indeed be non-deterministic, and thus cannot be learned by a deterministic learner.

##### 2. Incompatible input
This issue can happen when the answer to a new query is incompatible with the answer to a previous, shorter one. 
This is usually caused by the number of `minQueries` not being high enough, and thus not correctly capturing non-determinism. The safest option is to increase this parameter in the `config.yaml` and learn from scratch (by deleting the `output` folder and re-running).

