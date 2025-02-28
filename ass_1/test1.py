import numpy as np
import matplotlib.pyplot as plt

N = 3              # number of flows
C = 100.0          # link capacity (units per RTT)
ITER_MAX = 200
Q_star = 10.0      # desired queue occupancy
gamma = 0.1        # gain factor for rate adjustment

# initialize flow rates
R = np.ones(N) * 20.0  # start with some guess
Q_history = []
R_history = []

Q = 0.0  # queue occupancy in units

for t in range(ITER_MAX):
    # total offered load
    total_load = np.sum(R)
    
    # update queue
    if total_load > C:
        Q += (total_load - C)
    else:
        drain = min(Q, C - total_load)
        Q -= drain
    
    # store for plotting
    Q_history.append(Q)
    R_history.append(R.copy())
    
    # feedback for each flow (simplified: all flows see the same Q)
    for i in range(N):
        # HPCC-inspired rate update (very simplified)
        R[i] += gamma * (Q_star - Q)
        # ensure rates don't go negative
        R[i] = max(R[i], 0.0)

# plotting
plt.figure(figsize=(10,5))
plt.subplot(1,2,1)
plt.plot(Q_history, label="Queue Occupancy")
plt.axhline(Q_star, color='red', linestyle='--', label="Q* target")
plt.legend()
plt.title("Queue Occupancy Over Time")
plt.xlabel("Iteration")
plt.ylabel("Queue Size")

plt.subplot(1,2,2)
for i in range(N):
    plt.plot([rh[i] for rh in R_history], label=f"Flow {i+1}")
plt.title("Flow Rates Over Time")
plt.xlabel("Iteration")
plt.ylabel("Rate")
plt.legend()
plt.tight_layout()
plt.show()
