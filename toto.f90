program prec
  use precision
  use iso_fortran_env
  implicit none

  real(dp) :: x_pr, y_pr, z_pr
  real(4)  :: x_sp, y_sp, z_sp
  real(8)  :: x_dp, y_dp, z_dp
  real(16) :: x_qp, y_qp, z_qp
  double precision :: x_db, y_db, z_db
  
  x_pr = 0.12_dp; y_pr = 0.2_dp; z_pr = 0.1q0
  x_sp = 0.1_dp; y_sp = 0.1_sp; z_sp = 0.1q0
  x_dp = 0.1_dp; y_dp = 0.1_dp; z_dp = 0._dp
  x_qp = .1_dp; y_qp = .1_qp; z_qp = 34.1_dp
  x_db = 0._dp; y_db = 0.d0; y_db = 0.1_dp

  print*, x_pr, y_pr, z_pr
  print*, x_sp, y_sp, z_sp
  print*, x_dp, y_dp, z_dp
  print*, x_qp, y_qp, z_qp
  print*, x_db, y_db, z_db

end program prec
