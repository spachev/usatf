#! /usr/bin/perl

use Time::Piece;
my $now = Time::Piece->new;

print "place;div_place;name;age;gender;gun_time;pace\n";

my $skip_regex = qr/^\s*\d+.*\d+\:\d+/;
my $match_regex = qr/^\s*(\d+)\s+(\d+)\s([\w\-\']+\s[\w\-\']+)\s+(\d+)\s+([MF])\s+([\d\:]+)\s+(\d+\:\d+)/;

my $mode = "murray";

if ($ARGV[0] eq "xc")
{
	$mode = "xc";
	$skip_regex = qr/^\d+\s+/;
	$match_regex = qr/^\d+\s+(\w.*?),\s+(\w.*?)\s+(\d+).*(\d\:\d\d\.\d).*(\d\d\:\d\d\.\d)\s*$/;
}

my $line = 1;

while (<STDIN>)
{
	next unless /$skip_regex/;
	next unless /$match_regex/;
	my @a = ();
	if ($mode eq "xc")
	{
		push(@a, $line);
		push(@a, 0);
		push(@a, "$2 $1");
		push(@a, $now->year - $3 - 1900);
		push(@a, "M"); # TODO: handle gender properly
		push(@a, $5);
		push(@a, $4);
	}
	else
	{
		foreach my $i (1..7)
		{
			push(@a, $$i);
		}
	}
	#my ($place, $div_place, $name, $gender, $time, $pace) = ($1, $2, $3, $4, $5, $6);
	print(join(';', @a)."\n");
	$line++;
}
