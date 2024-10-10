import simpy
import random

# Konstantinställningar
RANDOM_SEED = 42
NUM_COPIES = 1  # Antal kopior av varje bok
BOOK_TITLES = [
    "Det slutar med oss",
    "Det börjar med oss",
    "De fenomenala fruntimren på",
    "Döda kvinnor förlåter inte",
    "Jävla karlar"
]
LOAN_DURATION = 28  # Maximal lånetid i dagar
RETURN_PROB = 0.8  # Sannolikheten för att boken lämnas tillbaka i tid
SIM_TIME = 100  # Simuleringstid i dagar


def visitor(env, name, library, book_title):
    """Simulerar en besökare som vill låna en bok och senare lämna tillbaka den."""
    print(f'{env.now:.1f} - {name} önskar låna "{book_title}"')
    with library[book_title].request() as request:
        # Besökaren står i kö för att låna boken
        yield request
        print(f'{env.now:.1f} - {name} lånar "{book_title}"')
        
        # Lånetid
        loan_time = LOAN_DURATION
        yield env.timeout(loan_time)
        
        # Returnera boken med viss sannolikhet
        if random.uniform(0, 1) < RETURN_PROB:
            print(f'{env.now:.1f} - {name} lämnar tillbaka "{book_title}" i tid')
        else:
            # Om besökaren är försenad med att lämna tillbaka boken
            delay = random.randint(1, 7)
            yield env.timeout(delay)
            print(f'{env.now:.1f} - {name} lämnar tillbaka "{book_title}" försenat med {delay} dagar')


def setup(env, num_copies, book_titles):
    """Setup av biblioteket med resurser för varje bok."""
    # Skapa en resurs för varje bok i biblioteket
    library = {title: simpy.Resource(env, num_copies) for title in book_titles}
    
    # Generera besökare
    for i in range(10):  # Första 10 besökarna
        book = random.choice(book_titles)
        env.process(visitor(env, f'Besökare {i+1}', library, book))
    
    # Fortsätt skapa nya besökare under simuleringen
    while True:
        yield env.timeout(random.randint(1, 5))  # Ny besökare var 1-5 dag
        i += 1
        book = random.choice(book_titles)
        env.process(visitor(env, f'Besökare {i+1}', library, book))


# Starta simuleringen
print("Bibliotekssimulering startar...")
random.seed(RANDOM_SEED)
env = simpy.Environment()
env.process(setup(env, NUM_COPIES, BOOK_TITLES))

# Kör simuleringen
env.run(until=SIM_TIME)