# PROGNOSIS
### Black-Box Analysis of Network Protocol Implementations

```
implementations -> Different implementations to be learned.
adapters -> Protocol adapters for alphabet translation.
learner -> Java based abstract learner.
```

## Getting Started

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
    http3: 1 # Use HTTP3 (instead of HTTP2).
    tracing: 0 # Use debug tracing in output.
    waitTime: 400ms # Period of time to wait for a response from SUL.
    httpPath: / # HTTP base request path to query.
synthesizer:
    op1: 0
```

#### 3. Learn
We can now start the fully automated learning process with:
```
docker-compose up --remove-orphans
```
