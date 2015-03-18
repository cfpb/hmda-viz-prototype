import weighted
import numpy as np
vals = [34, 16, 100, 25, 240]
rates = [1.65, 3.0, 2.25, 1.8, 2.33]
ndvals = np.array(vals)
ndrates = np.array(rates)
print weighted.median(ndrates, ndvals)
print sorted(rates)

