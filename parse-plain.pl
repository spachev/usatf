#! /usr/bin/perl

print "place;div_place;name;age;gender;gun_time;pace\n";

while (<>)
{
	next unless /^\s*\d+.*\d+\:\d+/;
	next unless /^\s*(\d+)\s+(\d+)\s([\w\-\']+\s[\w\-\']+)\s+(\d+)\s+([MF])\s+([\d\:]+)\s+(\d+\:\d+)/;
	my @a = ();
	foreach my $i (1..7)
	{
		push(@a, $$i);
	}
	#my ($place, $div_place, $name, $gender, $time, $pace) = ($1, $2, $3, $4, $5, $6);
	print(join(';', @a)."\n");
}
