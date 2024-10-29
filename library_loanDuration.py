import simpy
import random
import matplotlib.pyplot as plt

# Constant settings
RANDOM_SEED = 42 
NUM_COPIES = 1  # Nb of copies
BOOK_TITLES = [
    "Book (server) 1",
    "Book (server) 2"
]
LOAN_DURATION = 6  # Loan-time in days (servertime) the one that changes in the artical
RETURN_PROB = 0.8  # Probability that the book will return
SIM_TIME = 365  # Simulation time in days
MAX_QUEUE_SIZE = 10  # Max nb of customers in line

# Variables for logging data
wait_times = {title: [] for title in BOOK_TITLES}
queue_drops = {title: 0 for title in BOOK_TITLES}
arrival_times = {title: [] for title in BOOK_TITLES}

def visitor(env, name, library, book_title):
    """Simulerar en besökare som vill låna en bok och senare lämna tillbaka den."""
    arrival_time = env.now
    queue_length = len(library[book_title].queue)
    
    # Log the arrival time to calculate the arrival rate
    arrival_times[book_title].append(arrival_time)
    
    # If queue is full, customer drops off (packet-drop)
    if queue_length >= MAX_QUEUE_SIZE:
        queue_drops[book_title] += 1
        print(f'{env.now:.1f} - {name} tried to loan "{book_title}" but queue is full (packet-drop)')
        return
    
    print(f'{env.now:.1f} - {name} wishes to loan "{book_title}"')
    with library[book_title].request() as request:
        # Customer queing to loan a book
        yield request
        wait_time = env.now - arrival_time
        wait_times[book_title].append(wait_time)
        print(f'{env.now:.1f} - {name} loans "{book_title}" (waitingtime: {wait_time:.1f} days)')
        
        # loan time
        loan_time = LOAN_DURATION
        yield env.timeout(loan_time)
        
        # Retun the book with specific probability
        if random.uniform(0, 1) < RETURN_PROB:
            print(f'{env.now:.1f} - {name} returns "{book_title}" in time')
        else:
            # If customer is late with the return of a book
            delay = random.randint(1, 7)
            yield env.timeout(delay)
            print(f'{env.now:.1f} - {name} returns "{book_title}" late, with {delay} days')

def setup(env, num_copies, book_titles):
    """Setup av biblioteket med resurser för varje bok."""
    # Create a resource for each book in the library
    library = {title: simpy.Resource(env, num_copies) for title in book_titles}
    
    # Ceep creating customers during simulation time
    i = 0
    while True:
        yield env.timeout(random.randint(1, 5))  # Ny besökare var 1-5 dag
        i += 1
        book = random.choice(book_titles)
        env.process(visitor(env, f'Visitor {i}', library, book))

# Start simulation
print("Simulation starts...")
random.seed(RANDOM_SEED)
env = simpy.Environment()
env.process(setup(env, NUM_COPIES, BOOK_TITLES))

# Run simulation
env.run(until=SIM_TIME)

# Calculations for M/M/1 Queue Statistics
arrival_rates = {title: len(arrival_times) / SIM_TIME for title, arrival_times in arrival_times.items()}
service_rates = {title: 1 / LOAN_DURATION for title in BOOK_TITLES}

# Log the Queue Statistics
queue_statistics = {}
for title in BOOK_TITLES:
    λ = arrival_rates[title]  # Arrival rate
    μ = service_rates[title]  # Service rate
    ρ = λ / μ  # Intensity
    avg_wait_time = sum(wait_times[title]) / len(wait_times[title]) if wait_times[title] else 0
    max_wait_time = max(wait_times[title]) if wait_times[title] else 0
    
    queue_statistics[title] = {
        'λ': λ,
        'μ': μ,
        'ρ': ρ,
        'avg_wait_time': avg_wait_time,
        'max_wait_time': max_wait_time,
        'drops': queue_drops[title]
    }

# Show Queue Statistics
for title, stats in queue_statistics.items():
    print(f'\nQueue Statistics for {title}:')
    print(f"Arrival Rate (λ): {stats['λ']:.2f}")
    print(f"Service Rate (μ): {stats['μ']:.2f}")
    print(f"Intensity (ρ): {stats['ρ']:.2f}")
    print(f"Average Waiting Time: {stats['avg_wait_time']:.2f} days")
    print(f"Maximum Waiting Time: {stats['max_wait_time']:.2f} days")
    print(f"Nb of Packet-drops: {stats['drops']}")

# Visualize the results
plt.style.use('ggplot')

# Average, Max, and Min waiting time for each book
plt.figure(figsize=(10, 6)) 
bar_width = 0.15 
index = range(len(BOOK_TITLES))

avg_wait_times = [sum(wait_times[title]) / len(wait_times[title]) if wait_times[title] else 0 for title in BOOK_TITLES]
max_wait_times = [max(wait_times[title]) if wait_times[title] else 0 for title in BOOK_TITLES]
min_wait_times = [min(wait_times[title]) if wait_times[title] else 0 for title in BOOK_TITLES]

plt.bar([i - bar_width for i in index], avg_wait_times, bar_width, color='#6baed6', label='Average Wait Time')
plt.bar(index, max_wait_times, bar_width, color='#fd8d3c', label='Max Wait Time')
plt.bar([i + bar_width for i in index], min_wait_times, bar_width, color='#74c476', label='Min Wait Time')

plt.xticks(index, BOOK_TITLES, fontsize=16)
plt.ylabel('Waiting Time (days)', fontsize=16, fontweight='bold')  # Tjockare text för y-axeln
plt.yticks(fontsize=14, fontweight='bold')  # Tjockare text för y-axelns siffror
plt.title('Waiting Time for Each Book (Server)', fontsize=20, fontweight='bold')  # Tjockare text för titeln
plt.legend(fontsize=14)
plt.tight_layout()
plt.show()

# Visualize packet-drops for each book
plt.figure(figsize=(10, 6))
plt.bar(queue_drops.keys(), queue_drops.values(), color='#9e9ac8', width=0.5)
plt.xlabel('Book (Server)', fontsize=16, fontweight='bold')
plt.ylabel('Number of Packet-Drops', fontsize=16, fontweight='bold')
plt.yticks(fontsize=14, fontweight='bold')
plt.title('Number of Packet-Drops per Book (Server)', fontsize=20, fontweight='bold')
plt.xticks(fontsize=16)
plt.tight_layout()
plt.show()
