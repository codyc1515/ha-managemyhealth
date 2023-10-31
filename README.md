![Company logo](https://www.managemyhealth.co.nz/app/themes/mmh-child/assets/img/icons/logo-title-dark.svg)

# ManageMyHealth integration for Home Assistant
View the date and time of your next appointment.

## Getting started
In your configuration.yaml file, add the following:

```
sensor:
  - platform: managemyhealth
    email: joe@mama.com
    password: my-secure-password
```

## Installation
### HACS (recommended)
1. [Install HACS](https://hacs.xyz/docs/setup/download), if you did not already
2. [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=codyc1515&repository=ha-managemyhealth&category=integration)
3. Install the ManageMyHealth integration
4. Restart Home Assistant

### Manually
Copy all files in the custom_components/ha-managemyhealth folder to your Home Assistant folder *config/custom_components/managemyhealth*.

## Known issues
None known.

## Future enhancements
Your support is welcomed.
