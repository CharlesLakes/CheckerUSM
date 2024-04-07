class CheckerResponse:
  # Todos los status posibles, si no error
  available_status = ["NE", "AC", "WA", "RTE", "TLE", "CE", "SC"]

  """
  NE    No error
  AC    Accepted
  WA    Wrong answer
  RTE   Runtime error
  TLE   Time limit exceeded
  CE    Compilation error
  SC    Succesfully compilated
  """

  def __init__(self, status_code: str, content = None):
    if status_code not in self.available_status:
      raise Exception("Not available status code!")
    self.status_code = status_code
    self.content = content
	
  def set_status(self,status_code: str) -> None:
    self.status_code = status_code

  def get_status(self) -> str:
    return self.status_code