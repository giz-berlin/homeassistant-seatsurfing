# Seatsurfing Home Assistant integration

This Home Assistant integration displays all Seatsurfing spaces in Home Assistant.

## Imported data

Currently, for each space a binary occupancy sensor is created. It represents the current occupation of a space. Furthermore, the following attributes on the sensor are set:

* `current_user`: The current user occupying a seat (mail address)
* `current_booking_end`: Until when the current booking is running
* `current_subject`: User-entered subject of current booking
* `next_booking_start_date`: The datetime of the start date of the next booking
* `next_user`: The next user (mail address)
* `next_subject`: User-entered subject of next booking
