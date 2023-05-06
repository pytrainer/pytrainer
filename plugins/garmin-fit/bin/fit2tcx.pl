#!/usr/bin/env perl
use strict;
use warnings;

our $VERSION = '1.09';

=encoding utf-8

=head1 NAME

fit2tcx.pl - script to convert a FIT file to a TCX file

=head1 SYNOPSIS

    fit2tcx.pl [ --must=$list --tp_exclude=$list --indent=# --verbose ] $fit_activity_file [ $new_filename ]
    fit2tcx.pl --help
    fit2tcx.pl --version

=head1 DESCRIPTION

C<fit2tcx.pl> reads the contents of a I<$fit_activity_file> and converts it to correspoding TCX format. If <$new_filename> is provided, writes the resulting TCX content to it, otherwise prints the content to standard output.

=cut

use FindBin;
use lib $FindBin::Bin;

use Geo::FIT;
use POSIX qw(strftime);
use IO::Handle;
use FileHandle;
use Getopt::Long;
use Time::Local;

my ($must, $tp_exclude, $indent_n, $verbose, $version, $help) = ('Time', '', 2, 0);
sub usage { "Usage: $0 [ --help --must=\$list --tp_exclude=\$list --indent=# --verbose ] \$fit_activity_file [ \$new_filename ]\n" }

GetOptions( "must=s"       =>  \$must,
            "tp_exclude=s" =>  \$tp_exclude,
            "indent=i"     =>  \$indent_n,
            "verbose"      =>  \$verbose,
            "version"      =>  \$version,
            "help"         =>  \$help,
            )  or die usage();

if ($version) {
    print $0, " version: ", $VERSION, "\n";
    exit
}
die usage() if $help;

my ($from, $to) = qw(- -);
if (@ARGV) {
    $from = shift @ARGV;
    @ARGV and $to = shift @ARGV
}

# consider adding $double_precision to GetOptions(), renaming $pf to $print_format
my $double_precision = 7;
my $pf = $double_precision eq '' ? 'g' : '.' . $double_precision . 'f';

my (@must, @tp_exclude);
@must      = split /,/, $must;
@tp_exclude = split /,/, $tp_exclude;

=head2 Options

=over 4

=item C<< --must=I<list> >>

specifies a comma separated list of TCX elements which must be included in trackpoints.

C<fit2tcx.pl> convert each C<record> message to a trackpoint in TCX format, examines whether or not any of the elements in the list are defined, and drop the trackpoint if not.

Some map services seem to require a TCX file created with C<-must=Time,Position> option.

=item C<< --tp_exclude=I<list> >>

specifies a comma separated list of TCX elements which should be excluded from C<Trackpoint> elements in I<TCX file>.

For instance, with C<< --tp_exclude=AltitudeMeters >>, the resulting TCX file will contain no altitude data in it's C<Trackpoint>s.

=item C<< --indent=I<#> >>

specifies the number of spaces to use in indenting the XML tags of the TCX file.

=item C<< --verbose >>

shows FIT file header and trailing CRC information on standard output.

=back

=cut

# Parameters (were options in the initial version)
my $pw_fix = 1;
my $pw_fix_b = 0;
my $tplimit = 0;
my $tplimit_smart = 1;
my $include_creator = 1;
my $lap = '';
my $lap_start = 0;
my $lap_max = ~(~0 << 16) - 1;
my $tpmask = '';
my $tpfake = '';

# Parameters
my $tcdns = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2';
my $tcdxsd = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabasev2.xsd';
my $fcns = 'http://www.garmin.com/xmlschemas/FatCalories/v1';
my $fcxsd = 'http://www.garmin.com/xmlschemas/fatcalorieextensionv1.xsd';
my $tpxns = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2';
my $tpxxsd = 'http://www.garmin.com/xmlschemas/ActivityExtensionv2.xsd';
my $lxns = $tpxns;
my $lxxsd = $tpxxsd;
my (%xmllocation, @xmllocation);
$xmllocation{$tpxns} = $tpxxsd;
push @xmllocation, $tpxns, $tpxxsd;
$xmllocation{$fcns} = $fcxsd;
push @xmllocation, $fcns, $fcxsd;
$xmllocation{$lxns} = $lxxsd;
push @xmllocation, $lxns, $lxxsd;
$xmllocation{$tcdns} = $tcdxsd;
push @xmllocation, $tcdns, $tcdxsd;

my $indent = ' ' x $indent_n;

my $start = <<EOF;
<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<TrainingCenterDatabase xmlns="$tcdns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="@xmllocation">
$indent<Activities>
EOF

my $end = <<EOF;
$indent</Activities>
</TrainingCenterDatabase>
EOF

$indent .= ' ' x $indent_n;

my @with_ushort_value_def = ('sub' => [+{'name' => 'Value', 'format' => 'u'}]);

my %activity_def = (
    'name' => 'Activity',
    'array' => 1,
    'attr' => [+{'name' => 'Sport', 'format' => 's'}],
    'sub' => [
        +{'name' => 'Id', 'format' => 's'},
        +{
            'name' => 'Lap',
            'array' => 1,
            'attr' => [+{'name' => 'StartTime', 'format' => 's'}],
            'sub' => [
                +{'name' => 'TotalTimeSeconds', 'format' => $pf},
                +{'name' => 'DistanceMeters', 'format' => $pf},
                +{'name' => 'MaximumSpeed', 'format' => $pf},
                +{'name' => 'Calories', 'format' => 'u'},
                +{'name' => 'AverageHeartRateBpm', @with_ushort_value_def},
                +{'name' => 'MaximumHeartRateBpm', @with_ushort_value_def},
                +{'name' => 'Intensity', 'format' => 's'},
                +{'name' => 'Cadence', 'format' => 'u'},
                +{'name' => 'TriggerMethod', 'format' => 's'},
                +{
                    'name' => 'Track',
                    'array' => 1,
                    'sub' => [
                        +{
                            'name' => 'Trackpoint',
                            'array' => 1,
                            'sub' => [
                                +{'name' => 'Time', 'format' => 's'},
                                +{
                                    'name' => 'Position',
                                    'sub' => [
                                        +{'name' => 'LatitudeDegrees', 'format' => $pf},
                                        +{'name' => 'LongitudeDegrees', 'format' => $pf},
                                    ],
                                },
                                +{'name' => 'AltitudeMeters', 'format' => $pf},
                                +{'name' => 'DistanceMeters', 'format' => $pf},
                                +{'name' => 'HeartRateBpm', @with_ushort_value_def},
                                +{'name' => 'Cadence', 'format' => 'u'},
                                +{
                                    'name' => 'Extensions',
                                    'sub' => [
                                        +{
                                            'name' => 'TPX',
                                            'attr' => [+{'name' => 'xmlns', 'fixed' => $tpxns}],
                                            'sub' => [
                                                +{'name' => 'Speed', 'format' => $pf},
                                                +{'name' => 'Watts', 'format' => 'u'},
                                            ],
                                        },
                                    ],
                                },
                            ],
                        },
                    ],
                },

                +{
                    'name' => 'Extensions',
                    'sub' => [
                        +{
                            'name' => 'FatCalories',
                            'attr' => [+{'name' => 'xmlns', 'fixed' => $fcns}],
                            @with_ushort_value_def,
                        },
                        +{
                            'name' => 'LX',
                            'attr' => [+{'name' => 'xmlns', 'fixed' => $lxns}],
                            'sub' => [
                                +{'name' => 'AvgSpeed', 'format' => $pf},
                                +{'name' => 'MaxBikeCadence', 'format' => 'u'},
                                +{'name' => 'AvgWatts', 'format' => 'u'},
                                +{'name' => 'MaxWatts', 'format' => 'u'},
                            ],
                        },
                    ],
                },
            ],
        },

        +{
            'name' => 'Creator',
            'attr' => [+{'name' => 'xsi:type', 'fixed' => 'Device_t'}],
            'sub' => [
                +{'name' => 'Name', 'format' => 's'},
                +{'name' => 'UnitId', 'format' => 'u'},
                +{'name' => 'ProductID', 'format' => 'u'},
                +{'name' => 'Version',
                    'sub' => [
                        +{'name' => 'VersionMajor', 'format' => 's'},
                        +{'name' => 'VersionMinor', 'format' => 's'},
                    ],
                },
            ],
        },
    ],
    );

my @lap;
for my $beg_end (split /,/, $lap, -1) {
    if ($beg_end =~ /-/) {
        push @lap, $`, $'
    } else {
        push @lap, $beg_end, $beg_end
    }
}

if (@lap && $lap_start > 0) {
    for (my $i = 0 ; $i < @lap ; ++$i) {
        if ($lap[$i] =~ /^(\*|all)?$/i) {
            $lap[$i] = $i % 2 ? $lap_max : 0
        } else {
            $lap[$i] -= $lap_start
        }
    }
}

sub cmp_long {
    my ($a, $b) = @_;

    if ($a < $b) {
        if ($a - $b <= -180) {
            1
        } else {
            -1
        }
    } elsif ($a > $b) {
        if ($a - $b >= 180) {
            -1
        } else {
            1
        }
    } else {
        0
    }
}

sub tpmask_rect {
    my ($lat, $lon, $lat_sw, $lon_sw, $lat_ne, $lon_ne) = @_;
    $lat >= $lat_sw && $lat <= $lat_ne && &cmp_long($lon, $lon_sw) >= 0 && &cmp_long($lon, $lon_ne) <= 0
}

sub tpmask_make {
    my ($masks, $maskv) = @_;

    for my $mask (split /:|\s+/, $masks) {
        my @v = split /,/, $mask;

        if (@v % 2) {
            die "$mask: not a sequence of latitude and longitude pairs"
        } elsif (@v < 4) {
            die "$mask: \# of vertices < 2"
        } elsif (@v > 4) {
            die "$mask: sorry but arbitrary polygons are not implemented"
        } else {
            grep {
                s/^\s+|\s+$//g
            } @v;

            $v[0] > $v[2] and @v[0, 2] = @v[2, 0];
            &cmp_long($v[1], $v[3]) > 0 and @v[1, 3] = @v[3, 1];
            push @$maskv, [\&tpmask_rect, @v]
        }
    }
}

my @tpmask;
&tpmask_make($tpmask, \@tpmask);

my @tpfake;
&tpmask_make($tpfake, \@tpfake);

my $memo = { 'tpv' => [], 'trackv' => [], 'lapv' => [], 'av' => [] };
my $fit = new Geo::FIT;

$fit->use_gmtime(1);
$fit->numeric_date_time(0);
$fit->semicircles_to_degree(1);
$fit->without_unit(1);
$fit->mps_to_kph(0);

sub cb_file_id {
    my ($obj, $desc, $v, $memo) = @_;
    my $file_type = $obj->value_cooked(@{$desc}{qw(t_type a_type I_type)}, $v->[$desc->{i_type}]);

    if ($file_type eq 'activity') {
        1
    } else {
        $obj->error("$file_type: not an activity");
        undef
    }
}

sub cb_device_info {
    my ($obj, $desc, $v, $memo) = @_;

    if ($include_creator &&
            $obj->value_cooked(@{$desc}{qw(t_device_index a_device_index I_device_index)}, $v->[$desc->{i_device_index}]) eq 'creator') {
        my ($tname, $attr, $inval, $id) = (@{$desc}{qw(t_product a_product I_product)}, $v->[$desc->{i_product}]);
        my $t_attr = $obj->switched($desc, $v, $attr->{switch});

        if (ref $t_attr eq 'HASH') {
            $attr = $t_attr;
            $tname = $attr->{type_name}
        }

        my $ver = $obj->value_cooked(@{$desc}{qw(t_software_version a_software_version I_software_version)}, $v->[$desc->{i_software_version}]);
        my ($major, $minor) = split /\./, $ver, 2;

        $memo->{Creator} = +{
            'Name' => $obj->value_cooked($tname, $attr, $inval, $id),
            'UnitId' => $v->[$desc->{i_serial_number}],
            'ProductID' => $id,
            'Version' => +{
                'VersionMajor' => $major,
                'VersionMinor' => $minor,
            }
        }
    }
    1
}

sub cb_record {
    my ($obj, $desc, $v, $memo) = @_;
    my (%tp, $lat, $lon, $speed, $watts);

    $tp{Time} = $obj->named_type_value($desc->{t_timestamp}, $v->[$desc->{i_timestamp}]);
    $memo->{id} = $tp{Time} if !defined $memo->{id};

    $lat = $obj->value_processed($v->[$desc->{i_position_lat}], $desc->{a_position_lat})
        if defined $desc->{i_position_lat} && $v->[$desc->{i_position_lat}] != $desc->{I_position_lat};

    $lon = $obj->value_processed($v->[$desc->{i_position_long}], $desc->{a_position_long})
        if defined $desc->{i_position_long} && $v->[$desc->{i_position_long}] != $desc->{I_position_long};

    defined $lat and defined $lon and $tp{Position} = +{'LatitudeDegrees' => $lat, 'LongitudeDegrees' => $lon};

    if (defined $desc->{i_enhanced_altitude} && $v->[$desc->{i_enhanced_altitude}] != $desc->{I_enhanced_altitude}) {
        $tp{AltitudeMeters} = $obj->value_processed($v->[$desc->{i_enhanced_altitude}], $desc->{a_enhanced_altitude})
    } elsif (defined $desc->{i_altitude} && $v->[$desc->{i_altitude}] != $desc->{I_altitude}) {
        $tp{AltitudeMeters} = $obj->value_processed($v->[$desc->{i_altitude}], $desc->{a_altitude})
    }

    $tp{DistanceMeters} = $obj->value_processed($v->[$desc->{i_distance}], $desc->{a_distance})
        if defined $desc->{i_distance} && $v->[$desc->{i_distance}] != $desc->{I_distance};

    if (defined $desc->{i_enhanced_speed} && $v->[$desc->{i_enhanced_speed}] != $desc->{I_enhanced_speed}) {
        $speed = $obj->value_processed($v->[$desc->{i_enhanced_speed}], $desc->{a_enhanced_speed})
    } elsif (defined $desc->{i_speed} && $v->[$desc->{i_speed}] != $desc->{I_speed}) {
        $speed = $obj->value_processed($v->[$desc->{i_speed}], $desc->{a_speed})
    }

    $tp{HeartRateBpm} = +{'Value' => $v->[$desc->{i_heart_rate}]} if defined $desc->{i_heart_rate} && $v->[$desc->{i_heart_rate}] != $desc->{I_heart_rate};
    $tp{Cadence} = $v->[$desc->{i_cadence}] if defined $desc->{i_cadence} && $v->[$desc->{i_cadence}] != $desc->{I_cadence};
    $watts = $v->[$desc->{i_power}] * $pw_fix + $pw_fix_b if defined $desc->{i_power} && $v->[$desc->{i_power}] != $desc->{I_power};

    if (defined $speed || defined $watts) {
        my %tpx;
        $tpx{Speed} = $speed if defined $speed;
        $tpx{Watts} = $watts if defined $watts;
        $tp{Extensions} = +{'TPX' => \%tpx}
    }

    my $miss;
    for my $k (@tp_exclude) {
        delete $tp{$k}
    }
    for my $k (@must) {
        defined $tp{$k} or ++$miss
    }
    push @{$memo->{tpv}}, \%tp if !$miss;
    1
}

sub track_end {
    my $memo = shift;
    my $ntps = @{$memo->{tpv}};

    if ($ntps) {
        my %track = ('Trackpoint' => [@{$memo->{tpv}}]);

        @{$memo->{tpv}} = ();
        $memo->{ntps} += $ntps;
        push @{$memo->{trackv}}, \%track
    }
}

sub cb_event {
    my ($obj, $desc, $v, $memo) = @_;
    my $event = $obj->named_type_value($desc->{t_event}, $v->[$desc->{i_event}]);
    my $event_type = $obj->named_type_value($desc->{t_event_type}, $v->[$desc->{i_event_type}]);

    if ($event_type eq 'stop_all') {
        &track_end($memo)
    }
    1
}

my %intensity = (
    'active' => 'Active',
    'rest' => 'Resting',
    );

my %lap_trigger = (
    'manual' => 'Manual',
    'distance' => 'Distance',
    'time' => 'Time',
    );

sub cb_lap {
    my ($obj, $desc, $v, $memo) = @_;
    &track_end($memo);

    if (@{$memo->{trackv}}) {
        my %lap = ('Track' => [@{$memo->{trackv}}]);

        @{$memo->{trackv}} = ();
        $lap{'<a>StartTime'} = $obj->named_type_value($desc->{t_start_time}, $v->[$desc->{i_start_time}]);
        $lap{TotalTimeSeconds} = $obj->value_processed($v->[$desc->{i_total_timer_time}], $desc->{a_total_timer_time});

        $lap{DistanceMeters} = $obj->value_processed($v->[$desc->{i_total_distance}], $desc->{a_total_distance})
            if defined $desc->{i_total_distance} && $v->[$desc->{i_total_distance}] != $desc->{I_total_distance};

        if (defined $desc->{i_enhanced_max_speed} && $v->[$desc->{i_enhanced_max_speed}] != $desc->{I_enhanced_max_speed}) {
            $lap{MaximumSpeed} = $obj->value_processed($v->[$desc->{i_enhanced_max_speed}], $desc->{a_enhanced_max_speed})
        } elsif (defined $desc->{i_max_speed} && $v->[$desc->{i_max_speed}] != $desc->{I_max_speed}) {
            $lap{MaximumSpeed} = $obj->value_processed($v->[$desc->{i_max_speed}], $desc->{a_max_speed})
        }

        $lap{Calories} = $v->[$desc->{i_total_calories}]
            if defined $desc->{i_total_calories} && $v->[$desc->{i_total_calories}] != $desc->{I_total_calories};

        $lap{Cadence} = $v->[$desc->{i_avg_cadence}] if defined $desc->{i_avg_cadence} && $v->[$desc->{i_avg_cadence}] != $desc->{I_avg_cadence};

        my $intensity = $obj->value_cooked(@{$desc}{qw(t_intensity a_intensity I_intensity)}, $v->[$desc->{i_intensity}]);

        defined ($lap{Intensity} = $intensity{$intensity}) or $lap{Intensity} = 'Active';

        my $lap_trigger = $obj->value_cooked(@{$desc}{qw(t_lap_trigger a_lap_trigger I_lap_trigger)}, $v->[$desc->{i_lap_trigger}]);

        defined ($lap{TriggerMethod} = $lap_trigger{$lap_trigger}) or $lap{TriggerMethod} = 'Manual';

        $lap{AverageHeartRateBpm} = +{'Value' => $v->[$desc->{i_avg_heart_rate}]}
            if defined $desc->{i_avg_heart_rate} && $v->[$desc->{i_avg_heart_rate}] != $desc->{I_avg_heart_rate};

        $lap{MaximumHeartRateBpm} = +{'Value' => $v->[$desc->{i_max_heart_rate}]}
            if defined $desc->{i_max_heart_rate} && $v->[$desc->{i_max_heart_rate}] != $desc->{I_max_heart_rate};

        my (%x, %lx);
        $x{FatCalories} = +{'Value' => $v->[$desc->{i_total_fat_calories}]}
            if defined $desc->{i_total_fat_calories} && $v->[$desc->{i_total_fat_calories}] != $desc->{I_total_calories};

        if (defined $desc->{i_enhanced_avg_speed} && $v->[$desc->{i_enhanced_avg_speed}] != $desc->{I_enhanced_avg_speed}) {
            $lx{AvgSpeed} = $obj->value_processed($v->[$desc->{i_enhanced_avg_speed}], $desc->{a_enhanced_avg_speed})
        } elsif (defined $desc->{i_avg_speed} && $v->[$desc->{i_avg_speed}] != $desc->{I_avg_speed}) {
            $lx{AvgSpeed} = $obj->value_processed($v->[$desc->{i_avg_speed}], $desc->{a_avg_speed})
        }

        $lx{MaxBikeCadence} = $v->[$desc->{i_max_cadence}] if defined $desc->{i_max_cadence} && $v->[$desc->{i_max_cadence}] != $desc->{I_max_cadence};
        $lx{AvgWatts} = $v->[$desc->{i_avg_power}] * $pw_fix + $pw_fix_b if defined $desc->{i_avg_power} && $v->[$desc->{i_avg_power}] != $desc->{I_avg_power};
        $lx{MaxWatts} = $v->[$desc->{i_max_power}] * $pw_fix + $pw_fix_b if defined $desc->{i_max_power} && $v->[$desc->{i_max_power}] != $desc->{I_max_power};
        %lx and $x{LX} = \%lx;
        %x and $lap{Extensions} = \%x;
        push @{$memo->{lapv}}, \%lap
    }
    1
}

my %sport = (
    'running' => 'Running',
    'cycling' => 'Biking',
    );

sub cb_session {
    my ($obj, $desc, $v, $memo) = @_;

    unless (@{$memo->{lapv}}) {
        &cb_lap($obj, $desc, $v, $memo) || return undef
    }

    if (@{$memo->{lapv}}) {
        my %activity;

        defined($activity{'<a>Sport'} = $sport{$obj->named_type_value($desc->{t_sport}, $v->[$desc->{i_sport}])}) or $activity{'<a>Sport'} = 'Other';
        $activity{Id} = $obj->named_type_value($desc->{t_start_time}, $v->[$desc->{i_start_time}]);
        $activity{Lap} = [@{$memo->{lapv}}];
        @{$memo->{lapv}} = ();
        $activity{Creator} = $memo->{Creator} if defined $memo->{Creator};
        push @{$memo->{av}}, \%activity
    }

    delete $memo->{Creator};
    1
}

sub output {
    my ($datum, $def, $indent, $T) = @_;

    if (ref $datum eq 'ARRAY') {
        for my $datum1 (@$datum) {
            &output($datum1, $def, $indent, $T)
        }
    } else {
        $T->print("$indent<$def->{name}");
        my $attrv = $def->{attr};

        if (ref $attrv eq 'ARRAY') {
            for my $attr (@$attrv) {
                my ($aname, $aformat, $afixed) = @{$attr}{qw(name format fixed)};

                $T->print(" $aname=\"");

                if (defined $afixed) {
                    $T->print($afixed)
                } elsif (defined $aformat) {
                    $T->printf("%$aformat", $datum->{'<a>' . $aname})
                }
                $T->print("\"")
            }
        }

        $T->print(">");

        my ($sub, $format) = @{$def}{qw(sub format)};

        if (defined $format and $format ne '') {
            $T->printf("%$format", $datum)
        } elsif (ref $sub eq 'ARRAY') {
            $T->print("\n");

            my $subindent = $indent . ' ' x $indent_n;
            my $i;

            for ($i = 0 ; $i < @$sub ;) {
                my $subdef = $sub->[$i++];
                my $subdatum = $datum->{$subdef->{name}};
                defined $subdatum and &output($subdatum, $subdef, $subindent, $T)
            }
            $T->print($indent)
        }
        $T->print("</$def->{name}>\n")
    }
}

$fit->data_message_callback_by_name('file_id',     \&cb_file_id,     $memo) or die $fit->error;
$fit->data_message_callback_by_name('device_info', \&cb_device_info, $memo) or die $fit->error;
$fit->data_message_callback_by_name('record',      \&cb_record,      $memo) or die $fit->error;
$fit->data_message_callback_by_name('event',       \&cb_event,       $memo) or die $fit->error;
$fit->data_message_callback_by_name('lap',         \&cb_lap,         $memo) or die $fit->error;
$fit->data_message_callback_by_name('session',     \&cb_session,     $memo) or die $fit->error;
$fit->file($from);
$fit->open || die $fit->error;

sub dead {
    my ($obj, $err) = @_;
    my ($p, $fn, $l, $subr, $fit);

    $err = $obj->{error} if !defined $err;
    (undef, $fn, $l) = caller(0);
    ($p, undef, undef, $subr) = caller(1);
    $obj->close;
    die "$p::$subr\#$l\@$fn: $err\n"
}

my ($fsize, $proto_ver, $prof_ver, $h_extra, $h_crc_expected, $h_crc_calculated) = $fit->fetch_header;

defined $fsize || &dead($fit);

my $protocol_version          = $fit->protocol_version( $proto_ver );
my ($prof_major, $prof_minor) = $fit->profile_version(  $prof_ver  );

if ($verbose) {
    printf "File size: %lu, protocol version: %u, profile_version: %u.%02u\n", $fsize, $protocol_version, $prof_major, $prof_minor;

    if ($h_extra ne '') {
        print "Hex dump of extra octets in the file header";

        my ($i, $n);
        for ($i = 0, $n = length($h_extra) ; $i < $n ; ++$i) {
            print "\n  " if !($i % 16);
            print ' ' if !($i % 4);
            printf " %02x", ord(substr($h_extra, $i, 1))
        }
        print "\n"
    }

    if (defined $h_crc_calculated) {
        printf "File header CRC: expected=0x%04X, calculated=0x%04X\n", $h_crc_expected, $h_crc_calculated
    }
}

1 while $fit->fetch;
$fit->EOF || &dead($fit);

if ($verbose) {
    printf "CRC: expected=0x%04X, calculated=0x%04X\n", $fit->crc_expected, $fit->crc;
    my $garbage_size = $fit->trailing_garbages;
    print "Trailing $garbage_size octets garbages skipped\n" if defined $garbage_size and $garbage_size > 0
}

$fit->close;

my $av = $memo->{av};

if (@$av) {
    my ($i, $j);

    for ($i = $j = 0 ; $i < @$av ; ++$i) {
        my $lv = $av->[$i]->{Lap};

        if (@lap) {
            my ($p, $q, $r);

            for ($p = $q = 0 ; $p < @$lv ; ++$p) {
                for ($r = 1 ; $r < @lap ; $r += 2) {
                    if ($p >= $lap[$r - 1] && $p <= $lap[$r]) {
                        $lv->[$q++] = $lv->[$p];
                        last
                    }
                }
            }
            splice @$lv, $q
        }
        @$lv and $av->[$j++] = $av->[$i]
    }
    splice @$av, $j
}

sub minus_long {
    my ($a, $b);

    $a -= $b;

    if ($a < -180) {
        $a += 360
    } elsif ($a > 180) {
        $a = 360 - $a
    }
    $a
}

if (@$av && (@tpmask || @tpfake)) {
    my ($i, $j, $tp_prev);

    for ($i = $j = 0 ; $i < @$av ; ++$i) {
        my $lv = $av->[$i]->{Lap};
        my ($p, $q);

        for ($p = $q = 0 ; $p < @$lv ; ++$p) {
            my $trkv = $lv->[$p]->{Track};
            my ($u, $v);

            for ($u = $v = 0 ; $u < @$trkv ; ++$u) {
                my $tpv =$trkv->[$u]->{Trackpoint};
                my ($r, $s);

                for ($r = $s = 0 ; $r < @$tpv ; ++$r) {
                    my $masked;

                    for my $mask (@tpmask) {
                        if ($mask->[0]->(@{$tpv->[$r]->{Position}}{qw(LatitudeDegrees LongitudeDegrees)}, @$mask[1 .. $#$mask])) {
                            $memo->{ntps} -= 1;
                            $masked = 1;
                            last
                        }
                    }

                    unless ($masked) {
                        my $tp_cur = $tpv->[$r]->{Position};
                        my ($cur_lat, $cur_long) = @$tp_cur{qw(LatitudeDegrees LongitudeDegrees)};

                        for my $mask (@tpfake) {
                            if ($mask->[0]->($cur_lat, $cur_long, @$mask[1 .. $#$mask])) {
                                my $y;

                                if (ref $tp_prev eq 'HASH') {
                                    my ($prev_lat, $prev_long) = @$tp_prev{qw(LatitudeDegrees LongitudeDegrees)};
                                    my $sq = ($prev_lat - $cur_lat) ** 2 + &minus_long($prev_long, $cur_long) ** 2;
                                    my (@x, $x_lat, $x_long);

                                    for $x_lat (@$mask[3, 1]) {
                                        my $x_sq = ($prev_lat - $x_lat) ** 2;

                                        if ($x_sq <= $sq) {
                                            my $diff_long = sqrt($sq - $x_sq);

                                            $x_long = $prev_long + $diff_long;
                                            $x_long >= 180 and $x_long -= 360;

                                            unless (&cmp_long($x_long, $mask->[2]) < 0) {
                                                &cmp_long($x_long, $mask->[4]) <= 0 and push @x, [$x_lat, $x_long];
                                                $x_long = $prev_long - $diff_long;
                                                $x_long < -180 and $x_long += 360;
                                                &cmp_long($x_long, $mask->[2]) >= 0 and &cmp_long($x_long, $mask->[4]) <= 0 and push @x, [$x_lat, $x_long]
                                            }
                                        }
                                    }

                                    for $x_long (@$mask[2, 4]) {
                                        my $x_sq = &minus_long($prev_long, $x_long) ** 2;

                                        if ($x_sq <= $sq) {
                                            my $diff_lat = sqrt($sq - $x_sq);

                                            $x_lat = $prev_lat + $diff_lat;

                                            unless ($x_lat < $mask->[1]) {
                                                $x_lat <= $mask->[3] and push @x, [$x_lat, $x_long];
                                                $x_lat = $prev_lat - $diff_lat;
                                                $x_lat >= $mask->[1] and $x_lat <= $mask->[3] and push @x, [$x_lat, $x_long]
                                            }
                                        }
                                    }

                                    @x or die sprintf("prev=(%g, %g), cur=(%g, %g), mask=(%g, %g, %g, %g): \@x must not be empty.\n",
$prev_lat, $prev_long, $cur_lat, $cur_long, @$mask[1 .. 4]);

                                    my $y_sq;

                                    $y = shift @x;
                                    $y_sq = ($y->[0] - $cur_lat) ** 2 + &minus_long($y->[1], $cur_long) ** 2;

                                    if ($y_sq > 0) {
                                        while (@x) {
                                            my $x_sq = ($x[0]->[0] - $cur_lat) ** 2 + &minus_long($x[0]->[1], $cur_long) ** 2;

                                            $x_sq < $y_sq and ($y, $y_sq) = ($x[0], $x_sq);
                                            shift @x
                                        }
                                    }
                                } else {
                                    ($y) = sort {
                                        (($a->[0] - $cur_lat) ** 2 + &minus_long($a->[1], $cur_long) ** 2)
                                            cmp (($b->[0] - $cur_lat) ** 2 + &minus_long($b->[1], $cur_long) ** 2)
                                            } ([$cur_lat, $mask->[4]], [$cur_lat, $mask->[2]], [$mask->[1], $cur_long], [$mask->[3], $cur_long])
                                }

                                @$tp_cur{qw(LatitudeDegrees LongitudeDegrees)} = @$y;
                                last
                            }
                        }
                        $tp_prev = $tp_cur;
                        $tpv->[$s++] = $tpv->[$r]
                    }
                }
                splice @$tpv, $s;
                @$tpv and $trkv->[$v++] = $trkv->[$u]
            }
            splice @$trkv, $v;
            @$trkv and $lv->[$q++] = $lv->[$p]
        }
        splice @$lv, $q;
        @$lv and $av->[$j++] = $av->[$i]
    }
    splice @$av, $j
}

if (@$av) {
    my $T = new FileHandle "> $to";

    defined $T || &dead($fit, "new FileHandle \"> $to\": $!");
    $T->print($start);

    my $skip;

    if ($tplimit > 0 && ($skip = $memo->{ntps} / $tplimit) > 1) {
        for my $a (@$av) {
            for my $l (@{$a->{Lap}}) {
                for my $t (@{$l->{Track}}) {
                    my $tpv = $t->{Trackpoint};
                    my ($j, @mv);

                    if ($tplimit_smart && defined $tpv->[0]->{AltitudeMeters}) {
                        for (my $i = 1 ; $i < $#$tpv ;) {
                            my $updown;

                            for ($j = $i + 1 ; $j < @$tpv ; ++$j) {
                                if (defined $tpv->[$j]->{AltitudeMeters}) {
                                    if (($updown = $tpv->[$j]->{AltitudeMeters} - $tpv->[$i]->{AltitudeMeters})) {
                                        last
                                    }
                                }
                            }

                            if ($updown) {
                                my $k;

                                for ($k = $j + 1 ; $k < @$tpv ; ++$k) {
                                    if (defined $tpv->[$k]->{AltitudeMeters}) {
                                        if (($tpv->[$k]->{AltitudeMeters} - $tpv->[$j]->{AltitudeMeters}) / $updown < 0) {
                                            last
                                        }
                                    }
                                }

                                if ($k < @$tpv && $k - $i > $skip) {
                                    push @mv, $k
                                }
                                $i = $j
                            } else {
                                last
                            }
                        }
                    }
                    push @mv, $#$tpv + 1;

                    for (my $i = $j = 1 ; @mv ;) {
                        my $m = shift @mv;
                        my $start = $i;
                        my $count;

                        for ($count = 0 ; $i < $m ; ++$j, ++$count) {
                            my $next = $start + int($count * $skip);
                            my ($k, $wsum, $wn, $csum, $cn);

                            for ($k = $i ; $k < $next && $k < $m ; ++$k) {
                                my ($x, $tpx, $w);

                                if (defined ($x = $tpv->[$k]->{Extensions}) &&
                                        defined ($tpx = $x->{TPX}) &&
                                        defined ($w = $tpx->{Watts})) {
                                    $wsum += $w;
                                    ++$wn
                                }

                                if (defined $tpv->[$k]->{Cadence}) {
                                    $csum += $tpv->[$k]->{Cadence};
                                    ++$cn
                                }
                            }

                            $tpv->[$j] = $tpv->[$k - 1];
                            $tpv->[$j]->{Extensions}->{TPX}->{Watts} = $wsum / $wn if $wn > 0;
                            $tpv->[$j]->{Cadence} = $csum / $cn if $cn > 0;
                            $i = $k
                        }
                    }
                    $j < @$tpv and splice @$tpv, $j
                }
            }
        }
    }

    for my $a (@$av) {
        &output($a, \%activity_def, $indent, $T)
    }
    $T->print($end);
    $T->close
}

=head1 DEPENDENCIES

L<Geo::FIT>

=head1 SEE ALSO

L<Geo::TCX>

=head1 BUGS AND LIMITATIONS

No bugs have been reported.

Please report any bugs or feature requests to C<bug-geo-gpx@rt.cpan.org>, or through the web interface at L<http://rt.cpan.org>.

=head1 AUTHOR

Originally written by Kiyokazu Suto C<< suto@ks-and-ks.ne.jp >>.

This version is maintained by Patrick Joly C<< <patjol@cpan.org> >>.

Please visit the project page at: L<https://github.com/patjoly/geo-fit>.

=head1 VERSION

1.09

=head1 LICENSE AND COPYRIGHT

Copyright 2022, Patrick Joly C<< patjol@cpan.org >>. All rights reserved.

Copyright 2016-2022, Kiyokazu Suto C<< suto@ks-and-ks.ne.jp >>. All rights reserved.

This module is free software; you can redistribute it and/or modify it under the same terms as Perl itself. See L<perlartistic>.

=head1 DISCLAIMER OF WARRANTY

BECAUSE THIS SOFTWARE IS LICENSED FREE OF CHARGE, THERE IS NO WARRANTY FOR THE SOFTWARE, TO THE EXTENT PERMITTED BY APPLICABLE LAW. EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT HOLDERS AND/OR OTHER PARTIES PROVIDE THE SOFTWARE "AS IS" WITHOUT WARRANTY OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE SOFTWARE IS WITH YOU. SHOULD THE SOFTWARE PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR, OR CORRECTION.

IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MAY MODIFY AND/OR REDISTRIBUTE THE SOFTWARE AS PERMITTED BY THE ABOVE LICENSE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL, OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR INABILITY TO USE THE SOFTWARE (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE SOFTWARE TO OPERATE WITH ANY OTHER SOFTWARE), EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

=cut

1;

