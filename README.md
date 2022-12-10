# check_temp
Temperature check for icinga7nagios. Performance data included. Thresholds used by sensors. 

Uses sysfs for data retrieval, so it's not necessary to have lm_sensors installed (although recommended for sensors-detect, which helps with loading appropriate kernel modules).

Dependencies
* Python >3.4
* NRPE, check_by_ssh, local or icinga agent
