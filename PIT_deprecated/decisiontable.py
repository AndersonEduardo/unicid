import pylightxl as xl

from operator import itemgetter

from parameters import *


class DecisionTable():

    def __init__(self, filepath:str) -> None:

        self.rules = list()
        self.actions = list()
        self.conditions = set()
        self.__filepath = filepath
        self.datatypes = self.__set_parameters_datatypes()


    def _rank(self, x, top_n=1):
        '''Rank the scored outputs, considering the User query.'''
        
        counter = 0
        output = list()
        last_score = None

        x = sorted(x, key=itemgetter('SCORE'), reverse=True)
            
        for i, d_i in enumerate(x):

            if i == 0:

                output.append(d_i)
                last_score = d_i.get('SCORE')
                counter += 1

            else:

                if last_score == d_i.get('SCORE'):

                    output.append(d_i)

                else:

                    if counter < top_n:

                        output.append(d_i)
                        last_score = d_i.get('SCORE')
                        counter += 1

                    else:

                        break

        return output


    def __set_parameters_datatypes(self) -> dict:

        return PARAMETERS_DATATYPES


    def set_datatype(self, parameter, value:list) -> list:

        if not isinstance(parameter, str) and \
           not isinstance(value, list):

            raise TypeError('`parameter` must be a python str, and `value` must be a python list.')

        datatype = self.datatypes.get(parameter)

        if datatype[0] == int:

            return [int(float(v)) for v in value]
        
        elif datatype[0] == float:

            return [float(v) for v in value]

        elif datatype[0] == str:

            return [str(v) for v in value]

        else:

            raise TypeError('The only supported datatypes are: int, float and str.')


    def load_xlsx(self) -> None:

        xlsx_file = xl.readxl(fn=self.__filepath)
        sheet_names = xlsx_file.ws_names


        for sheet_name in sheet_names:

            sheet_data = xlsx_file.ws(ws=sheet_name)

            condition_keys = [str(x).strip().upper() for x in sheet_data.row(1)][:4]
            action_keys = [str(x).strip().upper() for x in sheet_data.row(1)][4:]

            for i in range(2, len(sheet_data.col(col=1)) + 1):

                row_data = [str(x).strip() for x in sheet_data.row(i)]

                rule = {k:(row_data[i] if not isinstance(row_data[i], str) else row_data[i].lower()) for (i,k) in enumerate(condition_keys)}
                action = {k:row_data[i+4] for (i,k) in enumerate(action_keys)}

                self.rules.append(rule)
                self.actions.append(action)

            self.conditions.update(condition_keys)

        if (len(self.rules) == 0) or (len(self.actions) == 0) or (len(self.rules) != len(self.actions)):

            raise IndexError("`rules` and `actions` must have the same length.")


    def build(self) -> None:

        self.load_xlsx()


    def query(self, x:dict, top_n:int = 1) -> list:

        if not isinstance(x, dict):

            raise TypeError("`x` must be a python dict.")

        top_n = (top_n if top_n is not None else len(self.actions))

        output = self.actions.copy()

        for i in range(len(self.rules)):

            score = sum([value in self.rules[i].values() for value in x.values()])

            output[i]['SCORE'] = score

        return self._rank(output, top_n)
