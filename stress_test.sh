#Full System Stress Test (2+ hours)
stress-ng --cpu 0 --cpu-method all --vm 4 --vm-bytes 85% --io 4 --hdd 2 --timeout 2h --metrics-brief

#CPU & Temperature Test (1+ hour)
stress-ng --cpu 0 --cpu-method all --timeout 1h --metrics-brief

#Monitor temperatures with:
watch -n 2 sensors

# RAM Test (1-2 hours)
stress-ng --vm 4 --vm-bytes 90% --timeout 2h --metrics-brief

# Power Supply Stability Test (3+ hours)
stress-ng --cpu 0 --vm 4 --vm-bytes 75% --io 4 --hdd 2 --gpu 1 --timeout 3h --metrics-brief
