face_id=2;
rotation_id=0;
base_folder='DiF'
file_name=sprintf('%07d-%02d',face_id,rotation_id);

M = csvread(sprintf('%s/points/%s.pts',base_folder,file_name));
X = M(:,1)
Y = M(:,2)
img = imread(sprintf('%s/cropped/%s.jpg',base_folder,file_name));
figure
imshow(img);
hold on;
plot(X(1:17),Y(1:17),'-x','MarkerSize',10,'LineWidth',5,'color','black')
plot(X(18:27),Y(18:27),'-x','MarkerSize',10,'LineWidth',5,'color','black')
plot(X(28:36),Y(28:36),'-x','MarkerSize',10,'LineWidth',5,'color','black')
plot(X(37:42),Y(37:42),'-x','MarkerSize',10,'LineWidth',5,'color','black')
plot(X(43:48),Y(43:48),'-x','MarkerSize',10,'LineWidth',5,'color','black')
plot(X(49:68),Y(49:68),'-x','MarkerSize',10,'LineWidth',5,'color','black')
uiwait(msgbox('Locate the point'));

