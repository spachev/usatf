#! /usr/bin/perl

my $first = 1;

while (<>)
{
	my @parts = split(/ /);

	if ($first)
	{
		print(join(';', @parts));
		$first = 0;
		next;
	}

	my $n_parts = scalar @parts;
	my $end_name_part = $n_parts - 4;
	print join(';', @parts[0..1]).";".join(' ', @parts[2..$end_name_part] ).";"
		.join(";", @parts[$end_name_part+1..$n_parts-1]);
}
