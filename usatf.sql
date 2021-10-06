drop table if exists `member`;
create table `member`
(
	`id` int unsigned not null auto_increment primary key,
	`usatf_no` bigint not null unique key,
	`fname` varchar(50) not null,
	`mname` varchar(50) not null,
	`lname` varchar(50) not null,
	`name_suffix` varchar(10) not null,
	`city` varchar(50) not null,
	`gender` enum('M','F') not null,
	`bdate` date not null
) engine=MyISAM;

drop table if exists `race`;
create table `race`
(
	`id` int unsigned not null auto_increment primary key,
 `name` varchar(255) not null,
 `date` date not null,
 `dist_cm` int unsigned not null,
 key(name),
 key(`date`)
) engine=myisam;

drop table if exists `race_results`;
create table `race_results`
(
	`race_id` int unsigned not null,
	`member_id` int unsigned not null,
	`chip_time_ms` int unsigned not null,
	`gun_time_ms` int unsigned not null,
	`age_grade` real not null,
	`place_overall` int unsigned not null,
	`place_overall_usatf` int unsigned not null,
 	`place_gender` int unsigned not null,
 	`place_div` int unsigned not null,
 	`place_gender_usatf` int unsigned not null,
 	`place_div_usatf` int unsigned not null,
 	`place_masters` int unsigned not null,
 	`place_masters_usatf` int unsigned not null,
 	`place_overall_age_grade` int unsigned not null,
 	`place_overall_age_grade_usatf` int unsigned not null,
 	`place_gender_age_grade` int unsigned not null,
 	`place_gender_age_grade_usatf` int unsigned not null,
 	primary key(race_id, member_id)
) engine=myisam;
