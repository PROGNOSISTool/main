#!/usr/bin/env bash
echo "LINES OF CODE:"
echo "Learner:"
cloc learner

echo "TCP Adapter:"
cloc adapters/tcp

echo "QUIC Adapter:"
cloc adapters/quic

echo "DIFF:"
echo "QUIC Adapter ~ QUIC Reference Implementation:"
cd adapters/quic && git diff --stat base main && cd ../..
