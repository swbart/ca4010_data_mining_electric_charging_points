SAVE_DIR=../data

# Back up SAVE_DIR
rm -rf $SAVE_DIR.bak
mv $SAVE_DIR/ $SAVE_DIR.bak/
rm -rf $SAVE_DIR

# Old script: (deprecated)
# # Get data for each country
# python ireland.py $SAVE_DIR/ireland

# # Combine datasets
# python combine.py $SAVE_DIR/final/dataset.csv $SAVE_DIR/ireland/ireland.csv

# Get data from all European countries based on OpenChargeMap
python openchargemap.py $SAVE_DIR/openchargemap

# Copy to expected final dataset destination
mkdir $SAVE_DIR/final
mv $SAVE_DIR/openchargemap/openchargemap.csv $SAVE_DIR/final/dataset.csv
