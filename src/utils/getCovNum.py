import os
from bs4 import BeautifulSoup as bs
from utils.Logger import getLogger

class getCovNum(object):
    def __init__(self) -> None:
        self.logger = getLogger()
        pass

    def getHtml(self, htmlPath: str) -> list:
        # return cov of index.html
        if not os.path.exists(htmlPath):
            self.logger.info(f'>>>>[getCpvNum] path:{htmlPath} not exits !')
            return [0,0,0]
        res = []
        with open(htmlPath, "r") as f:
            html = bs(f, 'html.parser')
            # it's len is 1, so just get the specified label
            tfoot = html.find_all("tfoot")[0]
            td_list = tfoot.find_all('td')
            # print(td_list)
            # get branch cov
            branch = str(td_list[3].string)
            r1 = branch.find('of')
            cov_branch = self.delete_commas(branch[r1+2:]) - self.delete_commas(branch[:r1])
            
            # get path cov
            cov_path = self.delete_commas(str(td_list[6].string)) - self.delete_commas(str(td_list[5].string))
            
            # get line cov
            cov_line = self.delete_commas(str(td_list[8].string)) - self.delete_commas(str(td_list[7].string))
            
            # print(cov_branch,cov_path, cov_line)
            res.append(cov_branch)
            res.append(cov_path)
            res.append(cov_line)
        return res
            
    def delete_commas(self, s: str) -> int:
        # delete commas
        res = ''
        for c in s:
            if c == ',' or c == ' ':
                continue
            else:
                res += c
        return int(res)

if __name__ == "__main__":
    g = getCovNum()
    g.getHtml("/home/hadoop/jacoco-0.8.7/cov-zookeeper-1/index.html")