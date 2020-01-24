import requests
import matplotlib.pyplot as plt
import json
import matplotlib.patches as mpatches

EARTH_RADIUS = 6.375e6 # meters
G = 6.67e-11
M = 5.97e24 # kg

SPACEX_API = r'https://api.spacexdata.com/v3/launches'
TELEMETRY_API_URL = r'https://api.launchdashboard.space/v1/launches/spacex'


def gravitational_acceleration(altitude):
    return -G*M/(EARTH_RADIUS+altitude) + G*M/EARTH_RADIUS


def specific_mechanical_energy(velocity: float, altitude: float) -> float:
    return 0.5*velocity**2 + gravitational_acceleration(altitude)


def fetch_meco_telemetry(flight_number: int) -> dict:
    url = TELEMETRY_API_URL + '?flight_number=' + str(flight_number) + '&event=meco'
    res = requests.get(url)
    res = res.json()

    if 'analysed' in res:
        return res['analysed'][0]['telemetry'][0]

def get_booster_from_flight_number(flight_number: int) -> str:
    url = SPACEX_API + '?flight_number=' + str(flight_number)
    return requests.get(url).json()[0]['rocket']['first_stage']['cores'][0]['core_serial']


def get_booster_and_energy(flight_number: int) -> tuple:
    booster = get_booster_from_flight_number(flight_number)
    meco_data = fetch_meco_telemetry(flight_number)

    if meco_data is None:
        return None, None

    velocity = meco_data['velocity']
    altitude = 1000*meco_data['altitude'] # converting the altitude to meters

    return booster, specific_mechanical_energy(velocity, altitude)


with open('launches.json') as f:
    booster_dict = json.load(f)

keys = sorted(list(booster_dict.keys()))


for i in range(4):
    xs = []
    heights = []
    boosters = []
    bottoms = []
    for x, key in enumerate(keys):
        if len(booster_dict[key]) > i:
            xs.append(x+1)
            heights.append(booster_dict[key][i]/1e6)
            bottoms.append(sum(booster_dict[key][0:i])/1e6)
            boosters.append(key)

    plt.bar(xs, heights, bottom=bottoms)

blue_patch = mpatches.Patch(color='b', label='First flight')
orange_patch = mpatches.Patch(color='orange', label='Second flight')
green_patch = mpatches.Patch(color='g', label='Third flight')
red_patch = mpatches.Patch(color='r', label='Fourth flight')

plt.legend(handles=[blue_patch, orange_patch, green_patch, red_patch])

plt.xticks(range(1, len(keys)+1), keys, rotation=45)
plt.ylabel('Energy [MJ/kg]')
plt.title('Recovery energy per Booster')
plt.show()