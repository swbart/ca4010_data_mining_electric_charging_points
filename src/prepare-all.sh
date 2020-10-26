SAVE_DIR=../data

# Back up SAVE_DIR
rm -rf $SAVE_DIR.bak
mv $SAVE_DIR/ $SAVE_DIR.bak/
rm -rf $SAVE_DIR

# Get data for each country
python ireland.py $SAVE_DIR/ireland

# Combine datasets
python combine.py $SAVE_DIR/final/dataset.csv $SAVE_DIR/ireland/ireland.csv
