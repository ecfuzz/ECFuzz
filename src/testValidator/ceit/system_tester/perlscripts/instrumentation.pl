####ConfuzzTestingStartSignal-1####
####Confuzz-code BEGIN1
my $line;
my $confuzz_flag_start=0;
my $confuzz_flag_exit=0;
my $confuzz_signal_to_start = "signal2start";
my $confuzz_signal_to_end = "signal2end";
my $confuzz_read_file = "< file2read";
my $confuzz_write_file = "> file2write";
open(DATA, $confuzz_write_file) or die "could not open!";
print DATA $confuzz_signal_to_start;
close(DATA);
while (1){
    sleep 1;
    open DATA, $confuzz_read_file;
    while($line=<DATA>){
    if ($line eq $confuzz_signal_to_start){
            $confuzz_flag_start = 1;
        }
    }
    close(DATA);
    if ($confuzz_flag_start == 1){
        last;
    }
}
####Confuzz-code END2
####ConfuzzTestingStartSignal-2####

#There are where the mod_perl code running

####ConfuzzTestingEndSignal-1####
####Confuzz-code BEGIN3
open(DATA, $confuzz_write_file) or die "could not open!";
print DATA $confuzz_signal_to_end;
close(DATA);
while (1){
    sleep 1;
    open DATA, $confuzz_read_file;
    while($line=<DATA>){
    if ($line eq $confuzz_signal_to_end){
            $confuzz_flag_exit = 1;
        }
    }
    close(DATA);
    if ($confuzz_flag_exit == 1){
        last;
    }
}
####Confuzz-code END4
####ConfuzzTestingEndSignal-2####