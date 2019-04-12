'''
    Hieu Do (hsd258)
    Finding code similarties
    Written to detect plagiarism in C++ programming assignments
'''

from fingerprint import fingerprint as FP
from collections import defaultdict

import os
import re

class CppFingerprint:
    def __init__(self):
        self.fn
        self.file_loc
        self.filestr_loc

class CodeSimilarityChecker:
    def __init__(self, window_len):
        self.window_len = window_len
        self.fingerprinter = FP.Fingerprint(kgram_len=5, window_len=window_len, base=10, modulo=1000)
        self.master_prints = defaultdict(list)

    def add_reference(self, reference_dir):
        for f in os.listdir(reference_dir):
            # Ignore hidden files
            if f.startswith('.'):
                continue

            print("Adding %s for reference" % f)
            fpath = os.path.join(reference_dir, f)
            ffile = self.fingerprinter.load_file(fpath)
            ffunc = self._extract_cpp_func(ffile)

            for ff in ffunc:
                func_body = ffile[ff[1]:ff[2]+1]
                clean_func = self._clean_up(func_body)

                fp = []
                try:
                    fp = self.fingerprinter.generate(str=clean_func)
                except FP.FingerprintException:
                    pass

                for hashval, pos in fp:
                    self.master_prints[hashval].append((f, ff[2], func_body, pos, clean_func))

    def check(self, check_file, threshold, output_dir):
        print("Checking %s against references" % check_file)
        ffile = self.fingerprinter.load_file(check_file)
        ffunc = self._extract_cpp_func(ffile)

        # Check each extracted function against the references to find matches
        outputfn = "check_{}.txt".format(check_file.split("/")[1])
        f = open(os.path.join(output_dir, outputfn), "w+")
        funcMatch = 0
        for ff in ffunc:
            func_body = ffile[ff[1]:ff[2]+1]
            clean_func = self._clean_up(func_body)

            fp = []
            try:
                fp = self.fingerprinter.generate(str=clean_func)
            except FP.FingerprintException:
                pass

            matchCnt = 0
            f.write("Analyzing %s\n" % ff[4])
            for hashval, pos in fp:
                if hashval in self.master_prints:
                    match = self.master_prints[hashval][0]
                    matchCnt += 1
                    f.write("Possible match of hash %d:\n%s:L%d: %s\n\n%s:L%d: %s\n" % \
                        (hashval, match[0], match[1], match[4][match[3]:match[3]+self.window_len], check_file, ff[2], clean_func[pos:pos+self.window_len]))

            if len(fp) == 0:
                f.write("NO MATCHES\n")
            elif matchCnt/len(fp) >= threshold:
                f.write("LOTS OF MATCHES\n")
                funcMatch += 1
            else:
                f.write("NOT ENOUGH MATCHES\n")
            f.write("===========================================\n")

        f.close()
        if funcMatch/len(ffunc) >= threshold:
            print("More than {:.0%} of all functions were matched".format(threshold))
        else:
            print("Less than {:.0%} of all functions could be matched".format(threshold))

    def _clean_up(self, line):
        line = ' '.join(line.split())
        return line

    def _extract_cpp_func(self, cpp_file):
        '''
            Use ReGex to find text matching pattern
            similar to function definition: string(string) {

            Group
            1 = return type
            2 = func name
            3 = param list
            4 = additional marking (ie, const method)
            5 = {
        '''
        all_func = []

        FUNC_PATTERN = "(.*) (.*)(\(.*\))(.*)({)"
        iter_obj = re.finditer(FUNC_PATTERN, cpp_file)
        last_close_bracket = -1 # assume a compilable c++ source (ie, the first function found is valid)
        for it in iter_obj:
            # Skip false positives (ie, if statements)
            if it.start() <= last_close_bracket:
                continue

            # Find the closing bracket of this function to detect false positives
            open_brack_cnt = 1
            func_body_pos = it.end()
            for i, c in enumerate(cpp_file[func_body_pos:]):
                if c == '{':
                    open_brack_cnt += 1
                elif c == '}':
                    open_brack_cnt -= 1

                if open_brack_cnt == 0:
                    last_close_bracket = func_body_pos +  i
                    break

            # begin of prototype - open bracket pos - close bracket pos - groups (1-5)
            tup = (it.start(), it.end()-1, last_close_bracket, it.group(1), it.group(2), it.group(3), it.group(4), it.group(5))
            all_func.append(tup)
        return all_func

def main():
    DATA_DIR = "dataset"
    csc = CodeSimilarityChecker(50)
    csc.add_reference(os.path.join(DATA_DIR, "reference"))

    print("\nChecking stage...")
    csc.check(os.path.join(DATA_DIR, "suspect_a.cpp"), 0.85, "output")
    csc.check(os.path.join(DATA_DIR, "suspect_b.cpp"), 0.85, "output")


if __name__ == "__main__":
    main()