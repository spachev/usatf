#! /usr/bin/perl

#! /usr/bin/perl

use strict;
use warnings;
use JSON qw( decode_json );
use Getopt::Long;
use WWW::Mechanize;

# https://www.irunutah.com/raceresults/?id=335

my $CB = "cb";
#my $KEY = "b03774892d16eb08c7ff6d62e3cb86ac";
my $KEY = "b0572ea058a1b55a7b4d9d18fc9c2630";
my $BASE_URL = "https://www.irunutah.com/raceresults/?id=";
my $race_id;
my $PLACE_POS = 1;
my $dist;

GetOptions("race-id=i" => \$race_id, "dist=i" => \$dist, "key=s" => \$KEY) or usage();

$dist or die "Missing --dist\n";
$race_id or die "Missing --race-id\n";
my $API_URL = "https://my3.raceresult.com/RRPublish/data/list.php?callback=".
	$CB."&key=".$KEY.
	"&listname=Result+Lists%7CAll+Finishers&page=results&contest=0&r=all&l=0&".
	"&eventid=";

my $m = new WWW::Mechanize();
my $event_id = get_event_id();
my $url = $API_URL.$event_id;
$m->get($url);
my $content = $m->content();
$content =~ /$CB\((.*)\)/ or die "Unexpected response from API: $content\n";
my $o = decode_json($1);
my $data = $o->{data};
my $key = find_race_key($data);
my $res = $data->{$key};
my $fields = "bib;place;bib;name;split_time;gun_time;chip_time;age;div_name;gender;".
	"\n";

print $fields;

foreach my $row (@$res)
{
	$row->[$PLACE_POS] = int($row->[$PLACE_POS]);
	my $line = join(';', @$row)."\n";
	print $line;
}

sub find_race_key
{
	my $data = shift;
	foreach my $k (keys %$data)
	{
		# TODO: when marathons and half marathons appear on itsyourrace, update this code
		return $k if $k =~ /^\#\d+\_(\d+)k$/i && $1 == $dist;
	}

	die "Nothing suitable in keys:".join(',', keys %$data)."\n";
}

sub usage
{
	print "Usage: ./$0 --race-id=val\n";
	exit(1);
}

sub get_event_id
{
	my $url = $BASE_URL.$race_id;
	$m->get($url);
	$m->content() =~ /new RRPublish.*\,\s*(\d+)\s*\,/ or
		die "Cannot extract event ID from content\n";
	return $1;
}
