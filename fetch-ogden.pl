#! /usr/bin/perl

use strict;
use warnings;
use HTML::TreeBuilder::XPath;

use WWW::Mechanize;
my $LAST_PAGE_START = 1101;
my $PAGE_SIZE = 100;
my $BASE_URL = "https://www.runraceresults.com/Secure/raceResultsAPI.cfm?do=race%3Aresults%3Aoneclick&EVID=RCQW2019&RCID=1&TYPE=overall";

my $DELIM = ";";

my $m = new WWW::Mechanize();
my @fields = ("place", "name", "chip_time", "gender", "age", "gun_time");

print(join($DELIM, @fields)."\n");

for (my $pos = 1; $pos <= $LAST_PAGE_START; $pos += $PAGE_SIZE)
{
	fetch_page($pos);
}

sub fetch_page
{
	my $page_start = shift;
	$m->get($BASE_URL."&SROW=$page_start");
	my $data = $m->content();
	#print($data);
	my $tree = HTML::TreeBuilder::XPath->new_from_content($data);
	my $rows = $tree->findnodes("//table[\@id='result-data']/tr");
	foreach my $r (@$rows)
	{
		my $cells = $r->findnodes("./td");
		my $n = scalar @$cells;
		next if ($n < 11);
		my $place = $cells->[0]->as_text();
		next if not ($place =~ /^\d+/);
		print(
			join($DELIM, map {my $res = $cells->[$_]->as_text();
				$res =~ s/\-/$DELIM/ if $_ == 7; $res;}
			grep { $_ < 2  or $_ == 4 or $_ == 7 or $_ == 9 } 0..($n-1))."\n");
	}
}
