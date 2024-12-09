# fmcobjectstocsv

Repository containing python app for accessing Cisco FMC via API and converting downloaded object to .csv.


Hardcoded parameters regarding FMC:
```
FMC_HOST='10.159.8.30'
FMC_ACCESS_POLICY_ID='ECF40C4C-9392-0ed3-0000-068720205318'
FMC_DOMAIN_ID='e276abec-e0f2-11e3-8169-6d9ed49b625f'
```

## Deployment

To deploy this project to Docker clone repository and run:

```bash
  docker build -t fmcobjectstocsv .
```

```bash
  docker run -p 8501:8501 fmcobjectstocsv
```

## Usage

Open in web browser:

example:
```
http://localhost:8501
```
```
http://<ip_address_of_server>:8501
```
