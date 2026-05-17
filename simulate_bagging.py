import numpy as np

def simulate_bags(total_dms=100, bias_pct=0.20, num_bags=1000):
    num_biased = int(total_dms * bias_pct)
    # 1 for biased, 0 for normal
    population = [1] * num_biased + [0] * (total_dms - num_biased)
    
    clean_bags = 0
    corrupted_bags = 0
    bag_corruptions = []
    
    for _ in range(num_bags):
        # sample with replacement, bag_size = total_dms
        bag = np.random.choice(population, size=total_dms, replace=True)
        biased_count = sum(bag)
        bag_corruptions.append(biased_count)
        
        if biased_count == 0:
            clean_bags += 1
        else:
            corrupted_bags += 1
            
    avg_corruption = np.mean(bag_corruptions)
    print(f"Total Bags: {num_bags}")
    print(f"Clean Bags (0 biased DMs): {clean_bags}")
    print(f"Corrupted Bags (>0 biased DMs): {corrupted_bags}")
    print(f"Average Biased DMs per Bag: {avg_corruption:.2f} ({avg_corruption/total_dms*100:.1f}%)")
    
if __name__ == "__main__":
    print("Simulation: 100 DMs, 20% bias")
    simulate_bags(100, 0.20)
    print("\nSimulation: 20 DMs, 25% bias")
    simulate_bags(20, 0.25)
