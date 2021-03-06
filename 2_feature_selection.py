# coding=utf-8

from sklearn.ensemble import GradientBoostingClassifier as GB
# from sklearn.ensemble import GradientBoostingRegressor as GB
model=GB(random_state=0)

# 交叉验证
from sklearn.model_selection import StratifiedKFold
cv=StratifiedKFold(n_splits=5, random_state=0, shuffle=False)
cross_val_score(model, train, train_y, cv=cv, scoring='precision').mean()# 'neg_mean_squared_error'


# 分类和回归--方差筛选(特征需离散化)
# var_cols 列名按照方差从小到大排序
var_cols=train.var().sort_values().index
train1=train.copy()
val1=val.copy()
i=-1
for col in var_cols:
    model=GB(random_state=0)
    model.fit(train1,train_y)
    pred=model.predict(val1)
    print i,np.sqrt(metrics.mean_squared_error(val_y,pred))
    print "_____________________________________" 
    train1=train1.drop(col,axis=1)
    val1=val1.drop(col,axis=1)
    i=i+1


		
# 分类--卡方检验
from sklearn.feature_selection import chi2
corrlation={}
for i in range(train.shape[1]):
    corrlation[train.columns[i]]=chi2(train,train_y)[0][i]
pd.DataFrame.from_dict(corrlation,orient='index').sort_values(by=[0],ascending=False)

def chi2_select(train,train_y):
	from sklearn.feature_selection import SelectKBest
	from sklearn.feature_selection import chi2
	score=0
	index=1
	for i in range(1,train.shape[1]+1):
		model=SelectKBest(chi2,k=i)
		train1=model.fit_transform(train,train_y)
		
		model=GB(random_state=0)
		cv_score=cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean()
		if score<cv_score:
			score=cv_score
			index=i
		print i,round(cv_score,4)
	print "______________________"
	print index,score
	# 被删除的特征
	model=SelectKBest(chi2,k=index).fit(train,train_y)
	train.columns[~model.get_support()]

# 回归--pearson系数筛选（|r|<=0.3为不存在线性相关；0.3<|r|<=0.5为低度线性相关；0.5<|r|<=0.8为显著线性相关；|r|>0.8为高度线性相关，r之和>1）	
from scipy.stats import pearsonr
cols=train.columns
corrlation={}
for col in cols:
    values=pearsonr(train[col],train_y)
    corrlation[col]=abs(values[0])
pd.DataFrame.from_dict(corrlation,orient='index').sort_values(by=[0],ascending=False)

# 回归--spearman系数筛选
from scipy.stats import spearmanr
cols=train.columns
corrlation={}
for col in cols:
    values=spearmanr(train[col],train_y)
    corrlation[col]=abs(values[0])
pd.DataFrame.from_dict(corrlation,orient='index').sort_values(by=[0],ascending=False)
	
# 分类和回归--最大信息系数,取值区间在[0，1],之和>1
from minepy import MINE
m=MINE()
cols=train.columns
corrlation={}
for col in cols:
    m.compute_score(train[col],train_y)
    corrlation[col]=m.mic()
pd.DataFrame.from_dict(corrlation,orient='index').sort_values(by=[0],ascending=False)

# 分类和回归--互信息法筛选
def mutual_info_select(train,train_y):
	from sklearn.feature_selection import SelectKBest
	from sklearn.feature_selection import mutual_info_classif
	score=0
	index=1
	for i in range(1,train.shape[1]+1):
		model=SelectKBest(mutual_info_classif,k=i)
		a_train=model.fit_transform(train,train_y)
		
		model = GB(random_state=0)
		cv_score=cross_val_score(model, a_train, train_y, cv=cv, scoring='recall').mean()
		if score<cv_score:
			score=cv_score
			index=i
		print i,round(cv_score,4)
	print "______________________"
	print index,score
	# 被删除的特征
	model=SelectKBest(mutual_info_classif,k=index).fit(train,train_y)
	train.columns[~model.get_support()]

# 分类和回归--基于相关系数的假设检验(分类-f_classif,回归-f_regression)
def f_classif_select(train,train_y):
	from sklearn.feature_selection import SelectKBest
	from sklearn.feature_selection import f_classif
	score=0
	index=1
	for i in range(1,train.shape[1]+1):
		model=SelectKBest(f_classif,k=i)
		train1=model.fit_transform(train,train_y)
		
		model = GB(random_state=0)
		cv_score=cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean()
		if score<cv_score:
			score=cv_score
			index=i
		print i,round(cv_score,4)
	print "______________________"
	print index,score
	model=SelectKBest(f_classif,k=index).fit(train,train_y)
	train.columns[~model.get_support()]
	
# 分类和回归--基于GDBT的单变量特征选择
model =GB(random_state=0)
scores=[]
columns=train.columns
corrlation={}
for i in range(train.shape[1]):
    score=cross_val_score(model,train.values[:,i:i+1],train_y.reshape(-1,1),scoring='recall',
                          cv=cv)
    corrlation[columns[i]]=format(np.mean(score),'.4f')
pd.DataFrame.from_dict(corrlation,orient='index').sort_values(by=[0],ascending=False)

# 分类和回归--递归特征消除
# 通过交叉验证自动确定消除特征数目
from sklearn.feature_selection import RFECV
model=RFECV(estimator=GB(random_state=0),step=1,cv=cv,scoring='recall')
model.fit(train,train_y)
# 被消除的特征
print train.columns[~model.support_],np.max(model.grid_scores_)

# 分类--基于L1的LR特征选择
def L1_select(train,train_y,a,b,step,c):
	from sklearn.feature_selection import SelectFromModel
	score=0
	index=0
	model1=LogsiticRegreesion(penalty="l1").fit(train.values, train_y.values.reshape(-1,1))
	for i in range(a,b,step):
		model = SelectFromModel(model1,threshold=i/c)
		model.fit(train,train_y)
		train1=model.transform(train)
		model =GB(random_state=0)
		cv_score=cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean()
		if score<cv_score:
			score=cv_score
			index=i/c
		print i/c,cv_score
	print
	print index,score

model1=LR(penalty="l1").fit(train.values, train_y.values.reshape(-1,1))
model = SelectFromModel(model1,threshold=index)
model.fit(train,train_y)
train1=model.transform(train)

model =GB(random_state=0)
print train.columns[~model.get_support()]
print round(cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean(),4)

# 分类和回归--基于GDBT输出特征重要性排序
model=GB(random_state=0)
model.fit(train,train_y)
fm_cols=pd.DataFrame(model.feature_importances_,index=train.columns).sort_values(by=0).index

train1=train.copy()
val1=val.copy()
i=0# i表示删了几个特征,按照特征重要性排序
for col in fm_cols:
    model=GB(random_state=0)
    model.fit(train1,train_y)
    pred=model.predict(val1)
    print i,np.sqrt(metrics.mean_squared_error(val_y,pred))
    print "_____________________________________" 
    train1=train1.drop(col,axis=1)
    val1=val1.drop(col,axis=1)
    i=i+1

# 分类和回归--基于GDBT的特征选择
def gdbt_select(train,train_y,a,b,step,c):
	from sklearn.feature_selection import SelectFromModel

	score=0
	index=0
	model1=GB(random_state=0).fit(train.values, train_y.values.reshape(-1,1))
	for i in range(a,b,step):
		model = SelectFromModel(model1,threshold=i/c)
		model.fit(train,train_y)
		train1=model.transform(train)
		model =GB(random_state=0)
		cv_score=cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean()
		if score<cv_score:
			score=cv_score
			index=i/c
		print i/c,cv_score
	print
	print index,score

model = SelectFromModel(model1,threshold=index)
model.fit(train,train_y)
train1=model.transform(train)

model =GB(random_state=0)
print train.columns[~model.get_support()]
print round(cross_val_score(model, train1, train_y, cv=cv, scoring='recall').mean(),4)

'''
### 小结
- 方差筛选
    - discarded feature: None
    - recall score: 
- 卡方检验
    - discarded feature: 
    - recall score:
- 互信息法
    - discarded feature: 
    - recall score:
- 基于相关系数的假设检验
    - discarded feature: 
    - recall score:
- 基于GDBT的单变量特征选择
    - discarded feature: 
    - recall score:
- 递归特征消除
    - discarded feature:
    - recall score:
- 基于L1的LR特征选择
    - discarded feature: 
    - recall score:
- 基于GDBT的特征选择
    - discarded feature:
    - recall score:
'''
