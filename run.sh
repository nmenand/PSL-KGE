#!/bin/bash

readonly BASE_DIR=$(realpath "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )")

readonly CLI_DIR="${BASE_DIR}/psl/cli"

readonly PSL_OUTPUT="psl_out"
readonly RESULTS_OUTPUT="results_out"
readonly RESULTS_POS_FILE="positive_evaluated_triples.txt"
readonly RESULTS_NEG_FILE="negative_evaluated_triples.txt"

function main() {
   trap exit SIGINT

   # Generate PSL
   generate::psl

   # Run PSL
   run::psl

   # Run evaluation
   evaluate::psl

   # Move results
   move::psl $@
}

function generate::psl() {
   echo "Generating PSL Files"
   ${BASE_DIR}/prepare_psl.sh config.json
}

function run::psl() {
   echo "Running PSL"
   pushd . > /dev/null

   cd ${CLI_DIR}
   ./run.sh > ${PSL_OUTPUT}.txt 2> ${PSL_OUTPUT}.err

   popd > /dev/null
}

function evaluate::psl() {
   echo "Evaluating PSL"
   ${BASE_DIR}/eval.sh config.json > ${RESULTS_OUTPUT}.out 2> ${RESULTS_OUTPUT}.err
}

function move::psl() {
   echo "Moving Results"
   local results_dir=${BASE_DIR}

   if [ $# == 1 ]; then
      results_dir=${BASE_DIR}/$1

      if [ -d ${results_dir} ]; then
         rm -r ${results_dir}
      fi

      mkdir ${results_dir}
   fi

   mv ${CLI_DIR}/${PSL_OUTPUT}.* ${results_dir}
   mv ${CLI_DIR}/inferred-predicates ${results_dir}

   mv ${RESULTS_OUTPUT}.* ${results_dir}
   mv ${RESULTS_POS_FILE} ${results_dir}
   mv ${RESULTS_NEG_FILE} ${results_dir}
}

main "$@"
