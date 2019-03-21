face_id=33001;

figure(1,'position',[400,400,1000,1000]);
for aug_id=[0:4]
	base_folder='/Volumes/SeanSSD/DiF/00034'
	file_name=sprintf('%07d-%02d',face_id,aug_id);

	M = csvread(sprintf('%s/%s.pts',base_folder,file_name));
	X = M(:,1)
	Y = M(:,2)
	img = imread(sprintf('%s/%s.jpg',base_folder,file_name));
	subplot(2,3,aug_id+1);
	imshow(img);
	hold on;
	plot(X(1:17),Y(1:17),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	plot(X(18:27),Y(18:27),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	plot(X(28:36),Y(28:36),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	plot(X(37:42),Y(37:42),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	plot(X(43:48),Y(43:48),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	plot(X(49:68),Y(49:68),'-*','MarkerSize',10,'LineWidth',5,'color','black')
	hold off;
endfor
uiwait(msgbox('Locate the point'));
