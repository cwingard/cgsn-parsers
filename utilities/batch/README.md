# Batch Harvesting

These scripts provide examples of how to collect the [OOI parsers](../harvesters/README.md) together into a single 
batch process to parse all the available data from an uncabled surface or profiler mooring on a per mooring/deployment 
basis. Within the Endurance and CGSN data teams, these example scripts are customized on a per-deployment basis in 
order to capture the variability of instrument availability and assignments that can occur between deployments. Those 
customizations are not included here, but the general structure of the batch process is.

The batch process is scheduled to run on a regular basis, typically every 30 minutes. The batch process is designed to 
be idempotent, meaning that it can be run multiple times without causing harm. Scheduling the batch process to run 
every 30 minutes allows the batch process to capture data shortly after it becomes available by using a SHA hash of the 
data directory to determine if new or updated data is available.

The batch jobs are all scheduled to run via cron, with each job running a single mooring/deployment. This allows for
concurrent processing of multiple moorings/deployments, which is important for the Endurance and CGSN data teams as
there are often multiple moorings/deployments that are active at the same time.

See the [README](../harvesters/README.md) in the harvesters directory for more information on the individual 
harvesters and the [repo README](../../README.md) for more information about this repo in general.
