# QUIC Learner
### Code and resources for model learning of QUIC implementations

```
implementation -> Different QUIC implementations to be learned.
adapter -> Go based adapter for QUIC learning.
learner -> Java based learner for QUIC learning.
resources -> Official IETF Drafts and related papers.
```

## Getting Started

The various components work together through Docker Compose. By switching the image tag of the implementation container in `docker-compose.yaml`, we can work on different QUIC implementations.
Available tags: `quiche`, `msquic`, `proxygen`, `googlequic`.

After that we can start the implementation and adapter with:
```
docker-compose up --remove-orphans adapter implementation
```

After this, we can pass "packet requests" to the adapter via a simple TCP connection. Something like:
```
telnet localhost 3333
> INITIAL(?,?)[CRYPTO]
```
The adapter woukd then concretise such packet, send it over, wait a fixed amount of time for replies, and send back the resulting symbols.

This process can be automated by using the `debug.TraceRunner` java program in the `learner` directory. Just create a `testtrace.txt` file in the same directory with a structure like:
```
10
INITIAL(?,?)[CRYPTO]
INITIAL(?,?)[CRYPTO]
HANDSHAKE(?,?)[ACK,CRYPTO]
HANDSHAKE(?,?)[ACK,HANDSHAKE_DONE]
SHORT(?,?)[ACK,STREAM]
SHORT(?,?)[ACK,STREAM]
SHORT(?,?)[ACK,STREAM]
SHORT(?,?)[ACK,STREAM]
SHORT(?,?)[ACK,STREAM]
SHORT(?,?)[ACK,STREAM]
```

And it will run this trace 10 times, and report back on the results. This is useful when debugging non-determinism. We can run the TraceRunner with:
```
java -cp "Learner/dist/QUICLearner.jar:Learner/lib/*" debug.TraceRunner Learner/input/config.yaml
```
