drop table if exists `member`;
create table `member`
(
	`id` int not null auto_increment primary key,
	`usatf_no` bigint not null unique key,
	`fname` varchar(50) not null,
	`mname` varchar(50) not null,
	`lname` varchar(50) not null,
	`name_suffix` varchar(10) not null,
	`city` varchar(50) not null,
	`gender` enum('M','F') not null,
	`bdate` date not null
) engine=MyISAM;
