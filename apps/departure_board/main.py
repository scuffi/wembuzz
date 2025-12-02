if __name__ == "__main__":
    from worker import get_arrivals, get_station_statuses, WembleyPark

    arrivals = get_arrivals(WembleyPark)
    print(arrivals)
    station_statuses = get_station_statuses(WembleyPark)
    print(station_statuses)
