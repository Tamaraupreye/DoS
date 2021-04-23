### Import Statements

import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

### Read Data for Detection

data = pd.read_csv("detect_data.csv")
X = data.drop(['Attack'], axis=1)
y = data.Attack

### Split into Training and Test Data

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

### Preprocessing Step

# sc = StandardScaler()
# X_train = sc.fit_transform(X_train)
# X_test = sc.transform(X_test)

### Train the Random Forest model

rf = RandomForestClassifier(n_estimators=20, random_state=0)
rf.fit(X_train, y_train)
rf.score(X_test, y_test)

### Export Model

dump(rf, "model.model")
