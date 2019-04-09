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
    def __init__(self):
        self.fingerprinter = FP.Fingerprint(kgram_len=5, window_len=4, base=10, modulo=1000)
        self.master_prints = defaultdict(list)
        self.base_prints = defaultdict(list)

    def add_base(self, base_file):
        pass

    def add_reference(self, reference_dir):
        for f in os.listdir(reference_dir):
            # Ignore hidden files
            if f.startswith('.'):
                continue

            print("Adding %s\n" % f)
            fpath = os.path.join(reference_dir, f)
            ffile = self.fingerprinter.load_file(fpath)
            fcomments = self._extract_comments(ffile)
            ffunc = self._extract_cpp_func(ffile)

            # for comment_pos, comment in fcomments:
            #     fp = self.fingerprinter.generate(str=comment)
            #     for hashval, pos in fp:
            #         self.master_prints[hashval].append((f, comment_pos, comment, pos))

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

    def check(self, check_file, threshold):
        ffile = self.fingerprinter.load_file(check_file)
        fcomments = self._extract_comments(ffile)
        ffunc = self._extract_cpp_func(ffile)

        # for comment_pos, comment in fcomments:
        #     fp = self.fingerprinter.generate(str=comment)
        #     if fp in self.master_prints:
        #         match = master_prints[fp][0]
        #         print("Possible match: %s:L%d: %s\n%s:%d\n" % (match[0], match[1], match[2], check_file, comment_pos, comment))

        for ff in ffunc:
            func_body = ffile[ff[1]:ff[2]+1]
            clean_func = self._clean_up(func_body)

            fp = []
            try:
                fp = self.fingerprinter.generate(str=clean_func)
            except FP.FingerprintException:
                pass

            for hashval, pos in fp:
                if hashval in self.master_prints:
                    match = self.master_prints[hashval][0]
                    print("Possible match:\n\
                            %s:L%d: %s\n\
                            %s:L%d: %s\n" % (match[0], match[1], match[2], \
                                            check_file, ff[2], func_body))
                    print("===========================================")

                    with open("res.txt", "a+") as f:
                        f.write("Possible match:\n%s:L%d: %s\n\n%s:L%d: %s\n" % \
                            (match[0], match[1], match[2], check_file, ff[2], func_body))
                        f.write("===========================================\n")

    def _clean_up(self, line):
        line = ' '.join(line.split())
        return line

    def _extract_comments(self, cpp_file):
        SINGLE_LINE_PATTERN = "(\/\/.*)"
        # MULTI_LINE_PATTER =
        single_comments = []
        iter_obj = re.finditer(SINGLE_LINE_PATTERN, cpp_file)
        for it in iter_obj:
            tup = (it.start(), it.group(1))
            single_comments.append(tup)
        return single_comments

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

def compare_fingerprint(fingerprints_a, fingerprints_b, filestr_a, filestr_b):
    checklist = defaultdict(list)
    for hashval, pos in fingerprints_a:
        checklist[hashval].append(pos)

    for hashval, pos in fingerprints_b:
        if checklist[hashval]:
            print("Found match %d:\nPosition %d: %s\nPosition %d: %s\n===========" % (hashval, pos, filestr_b[pos:pos+40], checklist[hashval][0], filestr_a[checklist[hashval][0]:checklist[hashval][0]+40]))


def main():
    DATA_DIR = "/Users/hieudosy/Google Drive/NYU/Academics/Spring 2019/6963 - Digital Forensics/final-project/code-similarities/dataset"
    csc = CodeSimilarityChecker()
    csc.add_reference(os.path.join(DATA_DIR, "reference"))
    csc.check(os.path.join(DATA_DIR, "hw04.cpp"), 85)


if __name__ == "__main__":
    main()