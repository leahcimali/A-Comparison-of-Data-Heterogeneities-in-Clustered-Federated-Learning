
import click

@click.command()
@click.option('--exp_type', help="The experiment type to run")
@click.option('--heterogeneity_type', help="The data heterogeneity to test (or dataset)")
@click.option('--dataset')
@click.option('--num_clients', type=int)
@click.option('--num_samples_by_label', type=int)
@click.option('--num_clusters', type=int)
@click.option('--centralized_epochs', type=int)
@click.option('--federated_rounds', type=int)
@click.option('--seed', type=int)



def main_driver(exp_type, dataset, heterogeneity_type, num_clients, num_samples_by_label, num_clusters, centralized_epochs, federated_rounds, seed):

    from pathlib import Path
    import pandas as pd

    from src.utils_logging import cprint, setup_logging
    from src.utils_data import setup_experiment, get_uid 

    setup_logging()

    row_exp = pd.Series({"exp_type": exp_type, "dataset": dataset, "heterogeneity_type": heterogeneity_type, "num_clients": num_clients,
               "num_samples_by_label": num_samples_by_label, "num_clusters": num_clusters, "centralized_epochs": centralized_epochs,
               "federated_rounds": federated_rounds, "seed": seed})
    

    output_name =  row_exp.to_string(header=False, index=False, name=False).replace(' ', "").replace('\n','_')

    hash_outputname = get_uid(output_name)

    pathlist = Path("results").rglob('*.json')

    for file_name in pathlist:

        if get_uid(str(file_name.stem)) == hash_outputname:

            cprint(f"Experiment {str(file_name.stem)} already executed in with results in \n {output_name}.json", lvl="warning")   
        
            return 
    try:
        
        model_server, list_clients = setup_experiment(row_exp)
    
    except Exception as e:

        cprint(f"Could not run experiment with parameters {output_name}. Exception {e}")

        return 
    
    launch_experiment(model_server, list_clients, row_exp, output_name)

    return          
            


def launch_experiment(model_server, list_clients, row_exp, output_name):
        
        from src.utils_training import run_cfl_client_side, run_cfl_server_side
        from src.utils_training import run_benchmark
        from src.utils_logging import cprint

        str_row_exp = ':'.join(row_exp.to_string().replace('\n', '/').split())

        if row_exp['exp_type'] == "benchmark":
            
            cprint(f"Launching benchmark experiment with parameters:\n{str_row_exp}", lvl="info")   

            run_benchmark(list_clients, row_exp, output_name, main_model=model_server)
            
        elif row_exp['exp_type'] == "client":
            
            cprint(f"Launching client-side experiment with parameters:\n {str_row_exp}", lvl="info")

            run_cfl_client_side(model_server, list_clients, row_exp, output_name)
            
        elif row_exp['exp_type'] == "server":

            cprint(f"Launching server-side experiment with parameters:\n {str_row_exp}", lvl="info")

            run_cfl_server_side(model_server, list_clients, row_exp, output_name)
            
        else:
            str_exp_type = row_exp['exp_type']
            raise Exception(f"Unrecognized experiement type {str_exp_type}. Please check config file and try again.")
        
        return




if __name__ == "__main__":
    main_driver()
