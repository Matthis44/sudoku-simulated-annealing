using System;
using System.Collections.Generic;
using System.Linq;
using System.Resources;
using System.Runtime.CompilerServices;
using System.Text;
using System.Threading.Tasks;
using Python.Runtime;
using Sudoku.Shared;
//using Sudoku.Z3Solvers;



namespace Sudoku.Recuit
{
	public class PythonRecuitDotNet : PythonSolverBase
	{

		public override Shared.SudokuGrid Solve(Shared.SudokuGrid s)
		{
			//System.Diagnostics.Debugger.Break();

			//For some reason, the Benchmark runner won't manage to get the mutex whereas individual execution doesn't cause issues
			//using (Py.GIL())
			//
			// create a Python scope
			using (PyModule scope = Py.CreateScope())
			{
				// convert the Person object to a PyObject
				PyObject pyCells = s.Cells.ToPython();
				// create a Python variable "person"
				scope.Set("sudoku", pyCells);
				// the person object may now be used in Python
				string code = Resources.sudoku;
				scope.Exec(code);

				var result = scope.Get("liste");
				var type = result.GetType();

				var managedResult = result.As<int[][]>();
				//var convertesdResult = managedResult.Select(objList => objList.Select(o => (int)o).ToArray()).ToArray();
				return new Shared.SudokuGrid() { Cells = managedResult };
			}

		}

		protected override void InitializePythonComponents()
		{
			InstallPipModule("numpy");
			base.InitializePythonComponents();
		}


	}

	public class PythonRecuitSimaneal : PythonSolverBase
	{

		public override Shared.SudokuGrid Solve(Shared.SudokuGrid s)
		{
			//System.Diagnostics.Debugger.Break();

			//For some reason, the Benchmark runner won't manage to get the mutex whereas individual execution doesn't cause issues
			//using (Py.GIL())
			//
			// create a Python scope
			using (PyModule scope = Py.CreateScope())
			{
				// convert the Person object to a PyObject
				PyObject pyCells = s.Cells.ToPython();

				// create a Python variable "person"
				scope.Set("instance", pyCells);


				string numpyConverterCode = Resources.numpy_converter;
				scope.Exec(numpyConverterCode);

				string recuitSolverCode = Resources.RecuitSimaneal;
				scope.Exec(recuitSolverCode);
				var result = scope.Get("r");
				var managedResult = result.As<int[]>().ToJaggedArray(9);
				//var convertedResult = managedResult.Select(objList => objList.Select(o => o.As<int>()).ToArray()).ToArray();
				return new Shared.SudokuGrid() { Cells = managedResult };
			}
		}

		protected override void InitializePythonComponents()
		{
			InstallPipModule("numpy");
			InstallPipModule("simanneal");
			base.InitializePythonComponents();
		}

	}
	public class PythonRecuitFaible : PythonSolverBase
	{

		public override Shared.SudokuGrid Solve(Shared.SudokuGrid s)
		{
			//System.Diagnostics.Debugger.Break();

			//For some reason, the Benchmark runner won't manage to get the mutex whereas individual execution doesn't cause issues
			//using (Py.GIL())
			//
			// create a Python scope
			using (PyModule scope = Py.CreateScope())
			{
				// convert the Person object to a PyObject
				PyObject pyCells = s.Cells.ToPython();
				// create a Python variable "person"
				scope.Set("sudoku", pyCells);
				// the person object may now be used in Python
				string code = Resources.RecuitSimule_faible;
				scope.Exec(code);

				var result = scope.Get("sol");
				var type = result.GetType();

				var managedResult = result.As<int[][]>();
				//var convertesdResult = managedResult.Select(objList => objList.Select(o => (int)o).ToArray()).ToArray();
				return new Shared.SudokuGrid() { Cells = managedResult };
			}
		}


		protected override void InitializePythonComponents()
		{
			InstallPipModule("numpy");
			base.InitializePythonComponents();
		}

	}
}



