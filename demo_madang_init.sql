/* DuckDB용 초기화 스크립트 (수정완료) */

-- 1. 기존 테이블 정리
DROP TABLE IF EXISTS Orders;
DROP TABLE IF EXISTS Book;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Imported_Book; 

-- 2. 테이블 생성
CREATE TABLE Book (
  bookid      INTEGER PRIMARY KEY,
  bookname    VARCHAR(40),
  publisher   VARCHAR(40),
  price       INTEGER 
);

CREATE TABLE Customer (
  custid      INTEGER PRIMARY KEY,  
  name        VARCHAR(40),
  address     VARCHAR(50),
  phone       VARCHAR(20)
);

CREATE TABLE Orders (
  orderid INTEGER PRIMARY KEY,
  custid  INTEGER,
  bookid  INTEGER,
  saleprice INTEGER,
  orderdate DATE,
  FOREIGN KEY (custid) REFERENCES Customer(custid),
  FOREIGN KEY (bookid) REFERENCES Book(bookid)
);

-- 3. 데이터 입력 (Book, Customer)
INSERT INTO Book VALUES(1, '축구의 역사', '굿스포츠', 7000);
INSERT INTO Book VALUES(2, '축구아는 여자', '나무수', 13000);
INSERT INTO Book VALUES(3, '축구의 이해', '대한미디어', 22000);
INSERT INTO Book VALUES(4, '골프 바이블', '대한미디어', 35000);
INSERT INTO Book VALUES(5, '피겨 교본', '굿스포츠', 8000);
INSERT INTO Book VALUES(6, '역도 단계별기술', '굿스포츠', 6000);
INSERT INTO Book VALUES(7, '야구의 추억', '이상미디어', 20000);
INSERT INTO Book VALUES(8, '야구를 부탁해', '이상미디어', 13000);
INSERT INTO Book VALUES(9, '올림픽 이야기', '삼성당', 7500);
INSERT INTO Book VALUES(10, 'Olympic Champions', 'Pearson', 13000);

INSERT INTO Customer VALUES (1, '박지성', '영국 맨체스타', '000-5000-0001');
INSERT INTO Customer VALUES (2, '김연아', '대한민국 서울', '000-6000-0001');  
INSERT INTO Customer VALUES (3, '장미란', '대한민국 강원도', '000-7000-0001');
INSERT INTO Customer VALUES (4, '추신수', '미국 클리블랜드', '000-8000-0001');
INSERT INTO Customer VALUES (5, '박세리', '대한민국 대전',  NULL);

-- 4. [중요] Orders 데이터 입력 (여기서 에러가 났던 겁니다!)
-- STR_TO_DATE(...) 부분을 싹 지우고 날짜 문자열만 남겼습니다.
INSERT INTO Orders VALUES (1, 1, 1, 6000, '2014-07-01'); 
INSERT INTO Orders VALUES (2, 1, 3, 21000, '2014-07-03');
INSERT INTO Orders VALUES (3, 2, 5, 8000, '2014-07-03'); 
INSERT INTO Orders VALUES (4, 3, 6, 6000, '2014-07-04'); 
INSERT INTO Orders VALUES (5, 4, 7, 20000, '2014-07-05');
INSERT INTO Orders VALUES (6, 1, 2, 12000, '2014-07-07');
INSERT INTO Orders VALUES (7, 4, 8, 13000, '2014-07-07');
INSERT INTO Orders VALUES (8, 3, 10, 12000, '2014-07-08'); 
INSERT INTO Orders VALUES (9, 2, 10, 7000, '2014-07-09'); 
INSERT INTO Orders VALUES (10, 3, 8, 13000, '2014-07-10');

-- 5. Imported_Book 테이블
CREATE TABLE Imported_Book (
  bookid      INTEGER,
  bookname    VARCHAR(40),
  publisher   VARCHAR(40),
  price       INTEGER 
);

INSERT INTO Imported_Book VALUES(21, 'Zen Golf', 'Pearson', 12000);
INSERT INTO Imported_Book VALUES(22, 'Soccer Skills', 'Human Kinetics', 15000);