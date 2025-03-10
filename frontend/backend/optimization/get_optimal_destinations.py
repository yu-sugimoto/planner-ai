import json
from typing import List, Dict

def load_transportation_data() -> List[Dict]:
    """Load transportation data from Osaka to all spots"""
    with open('data/Osaka_to_all_spots.json', 'r') as f:
        return json.load(f)

def optimize_itinerary(budget: int, days: int, city: str) -> List[Dict]:
    """
    Optimize itinerary to visit maximum number of spots within budget and time constraints
    Args:
        budget: Total budget in JPY
        days: Number of days for the trip
        city: City that the trip places in 
    Returns:
        List of daily itineraries
    """
    # Load transportation data
    data = load_transportation_data()
    
    # Initialize variables
    daily_time = 600  # 10 hours per day in minutes
    remaining_budget = budget
    itineraries = []
    
    # Create a list of spots sorted by efficiency (time per spot)
    spots = sorted(data, key=lambda x: x['transportation_time'] / (x['transportation_fare'] + 1))
    
    for day in range(1, days + 1):
        daily_itinerary = {
            'day': day,
            'destinations': []
        }
        
        remaining_time = daily_time
        current_location = "0"  # Starting from Osaka (string to match data format)
        
        while remaining_time > 0 and remaining_budget > 0:
            # Find the next spot that fits within remaining time and budget
            next_spot = None
            # Filter available spots
            available_spots = [
                spot for spot in spots
                if (spot['start_destination_id'] == current_location and
                    spot['transportation_time'] <= remaining_time and
                    spot['transportation_fare'] <= remaining_budget and
                    spot['end_destination_id'] not in [d for day in itineraries for d in day['destinations']])
            ]
            
            if available_spots:
                next_spot = available_spots[0]
            
            if not next_spot:
                break
                
            # Add spot to itinerary
            daily_itinerary['destinations'].append(next_spot['end_destination_id'])
            
            # Update remaining resources
            remaining_time -= next_spot['transportation_time']
            remaining_budget -= next_spot['transportation_fare']
            current_location = next_spot['end_destination_id']
        
        itineraries.append(daily_itinerary)
    
    return itineraries

def main():
    # Example usage
    budget = 50000  # 50,000 JPY
    days = 3  # 3 days
    
    itinerary = optimize_itinerary(budget, days)
    print(json.dumps(itinerary, indent=2))

if __name__ == '__main__':
    main()
