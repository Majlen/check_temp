# check_temp
Temperature check (not only) for nagios. Performance data included.

Uses sysfs for data retrieval, so it's not necessary to have lm_sensors installed (although recommended for sensors-detect, which helps with loading appropriate kernel modules).

Dependencies
* Python >3.4
* NRPE
