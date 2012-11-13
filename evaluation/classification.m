%%
function [] = classification(train_file,test_file,num_components)
	readRawDataFileName = train_file;
	fidRead = fopen(readRawDataFileName, 'r');
	data = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector1=[];
	for i = 1:num_components,
           featureVector1 = [featureVector1 data{i+1}];
        end
	gt1 = data{1};
	fclose(fidRead);
	
	readTestDataFileName = test_file;
	fidRead = fopen(readTestDataFileName, 'r');
	testData = textscan(fidRead, '%d %f %f %f %f %f %f %f %f %f', 'delimiter', ',');
	featureVector2=[];
	for i = 1:num_components,
           featureVector2 = [featureVector2 testData{i+1}];
        end
	gt2 = testData{1};
	fclose(fidRead);
	
	%%
	%Naive Bayes%
	%% modified to avoid zero variance %%
	
	trainGT = gt1(1,1);
	for i = 2: length(gt1),
		if gt1(i) ~= trainGT,
			testIndext = i;
			break;
		end
	end
	if var(featureVector1(i:end,3)) == 0,
		featureVector1(i,3) = featureVector1(i,3) + 0.0002;
	end
	if var(featureVector1(1:i,3)) == 0,
		featureVector1(1,3) = featureVector1(1,3) + 0.0002;
	end
	% end of modification
	BaysianObject = NaiveBayes.fit(featureVector1,gt1,'Prior','uniform'); %classLabel=  posterior(BaysianObject,testVector)
	classLabel=  BaysianObject.predict(featureVector2);
	cMat1 = confusionmat(gt2,classLabel,'ORDER',[0 1 2 3 4])
	
	for i = 1: size(cMat1,1),
	   accuracy(i) = cMat1(i,i)/sum(cMat1(i,1:end));
	end
	fprintf(1,'\nRESULT: Naive Bayes\t');fprintf(1,'%f \t',accuracy)
	fprintf(1,'\n');
	exit;
