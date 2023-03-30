# Generating Hubs

## New Hub Steps

### WashU

The general steps to add a WashU hub are:

1. Create a directory for the hub under `generation-data`

1. Add a template describing the tracks for each sample. Please use the format `$HUBNAME-washu-template.json` to name the template.

1. Add any extra input data the script may require (e.g. experiment IDs, experiment metadata) to the directory.

1. Write a script to generate the hub based on the template. Please use the format `$HUBNAME-washu-template.py`to name the template.

### UCSC

The current recommendation is to generate the WashU hubs first, and then use the `washu-to-ucsc.py` script to mirror that configuration.

## Existing Hub Updates

### ChromBPNet

#### WashU

```
python generation-data/chrombpnet/chrombpnet-washu-template.py -a generation-data/chrombpnet/atac-encs.txt -d generation-data/chrombpnet/dnase-encs.txt -o washu/chrombpnet-hub.json
```

#### UCSC

```
python scripts/washu-to-ucsc.py -i washu/chrombpnet-hub.json -o ucsc/chrombpnet-hub.txt
```