#!/usr/bin/perl -w

BEGIN {
  use strict;
  use Getopt::Long;

  sub run_debug   ($);
  sub print_debug ($);
}

# autoflush
$| = 1;




###################################################################
#
# get options and print help
#
my $name   = "m101";
my $survey = "2mass";
my $band   = "j";
my $x      = "1.0";
my $y      = "1.0";
my $cdelt  = "0.000278";
my $root   = `pwd`;
my $help   = 0;
my $debug  = 0;

chomp $root;

print "\n";


my $result = GetOptions ("name=s"   => \$name,
                         "survey=s" => \$survey,
                         "band=s"   => \$band,
                         "x=s"      => \$x,
                         "y=s"      => \$y,
                         "cdelt=s"  => \$cdelt,
                         "root=s"   => \$root,
                         "help"     => \$help,  
                         "debug"    => \$debug   
                       );

if ( ! $result || $help)
{
  print <<EOT;

    Usage: $0 [options]
    
    Options (with defaults given):
     -root   `pwd`/\$name.\$survey.\$x.\$y.\$cdelt
                            target directory
     -name   m101           data objstr (?)
     -survey 2mass          data survey
     -band   j              data band
     -x      1.0            data width
     -y      1.0            data height
     -cdelt  0.000278       data resolution (?)
     -debug                 prints some debug messages
     -help                  prints this message

   For more information, see man pages for mDAG and mArchiveList, 
   or the general Montage documentation.
  
EOT

  exit (! $help);
}


###################################################################
#
# main
#
my $tgt    = "$root/${name}_${survey}_${x}_${y}_${cdelt}"; 
my $data   = "$root/${name}_${survey}_${x}_${y}_${cdelt}/data"; 
my $list   = "$root/${name}_${survey}_${x}_${y}_${cdelt}/files.tbl"; 

print "tgt x:     : '$x'\n";
print "tgt y:     : '$y'\n";
print "tgt dir    : '$tgt'\n";
print "data dir   : '$data'\n";
print "file list  : '$list'\n\n";

if ( ! -d $tgt  ) { run_debug ("mkdir -v $tgt "); }
if ( ! -d $data ) { run_debug ("mkdir -v $data"); }


{
  # create dag and file list
  print "creating dag ......... "; 
  run_debug ("mDAG $survey $band $name $x $y $cdelt $tgt tmpurl test");
  print "done\n";
}


{
  print "fixing   dag ......... "; 
  # <job id="ID000210" name="mImgtbl" version="3.0" level="4" dv-name="mImgtbl1" dv-version="1.0">
  #   <argument>
  #     .
  #     -t <filename file="cimages_20091208_123627_56073.tbl"/>
  #     <filename file="newcimages.tbl"/>
  #   </argument>
  open (IN, "<$tgt/dag.xml") || die "Cannot open dag.xml: $!\n";
  my @lines = <IN>;
  chomp (@lines);
  close (IN);

  my $tmp = "";

  foreach my $i ( 0 .. $#lines )
  {
    if (   $lines[$i  ] =~ /^\s*<job id="(ID\d+)" name="mImgtbl"/io )
    {
      my $job = $1;
      if ( $lines[$i+1] =~ /^\s*<argument>\s*$/io                 &&
           $lines[$i+2] =~ /^\s*\./io                             &&
           $lines[$i+3] =~ /^\s*-t\s+<filename file="/io          )
      {
        print "$job ";
        $tmp         = $lines[$i+2];
        $lines[$i+2] = $lines[$i+3];
        $lines[$i+3] = $tmp;
      }
    }
  }

  open (OUT, ">$tgt/dag.xml") || die "Cannot open dag.xml: $!\n";
  foreach my $line ( @lines )
  {
    print OUT "$line\n";
  }
  close OUT;

  print " done\n";
}


{
  print "creating file list ... "; 
  run_debug ("mArchiveList $survey $band $name $x $y        $list");
  print "done\n";
}


# grep URLs from file list, to be fetched
{
  print "download data ........ \n"; 

  open (IN, "<$list") || die "Cannot open $list: $!\n";
  while ( <IN> )
  {
    if ( $_ =~ /^.*\s(http\S+)\s+(\S+).*$/ ) 
    { 
      print "   $2 ... "; 
      run_debug ("wget -q -c '$1' -O '$data/$2'");
      print "done\n"; 
    }
  }
  close IN;

  print "download data ........ done\n"; 
}


{
  print "rename hdr files ..... \n"; 
  my $base = qx {grep statfile $tgt/dag.xml | grep filename | grep input | cut -f 2 -d '"'};

  chomp ($base);
  $base =~ s/^statfile_(.+)\.tbl$/$1/g;

  print_debug ("base string: '$base'");

  run_debug ("cp $tgt/region.hdr    $data/region_$base.hdr");
  run_debug ("cp $tgt/cimages.tbl   $data/cimages_$base.tbl");
  run_debug ("cp $tgt/pimages.tbl   $data/pimages_$base.tbl");
  run_debug ("cp $tgt/statfile.tbl  $data/statfile_$base.tbl");
  print "done\n";
}

print "\n";



###################################################################
#
# subroutines
#
sub run_debug ($)
{
  my $cmd = shift;

  if ( $debug )
  {
    print "\n - debug : running '$cmd'\n";
  }

  `$cmd`;
}

sub print_debug ($)
{
  my $msg = shift;

  if ( $debug )
  {
    print "\n - debug : $msg\n";
  }
}

