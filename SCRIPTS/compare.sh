#!/bin/sh

module add python/3.8

# Run for phytoplankton
echo "Running for phytoplankton"

for (( i=0; i<52; i++ )); do
	echo ${i}

	./dominant-phyto.py ${i}
done

convert -delay 25 -loop 0 $(ls Dominant-species-phyto-*.png | sort -V) DOM-PHYTO.gif


# Run for zooplankton
echo ""
echo "Running for zooplankton"

for (( i=0; i<52; i++ )); do
	echo ${i}

	./dominant-zoo.py ${i}
done

convert -delay 25 -loop 0 $(ls Dominant-species-zoo-*.png | sort -V) DOM-ZOO.gif

echo "Finished"
