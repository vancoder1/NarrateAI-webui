import gradio as gr

class WebuiHandler:
    def __init__(self):
        self.model = None
        self.setup_interface()
        
    def setup_interface(self):
        self.inputs = [
            gr.components.File(label='Upload CSV'),
            gr.components.Number(value=30, label='Prediction Periods'),
        ]

        self.outputs = [
            gr.components.Plot(label='CSV Graph')
        ]
        
        self.interface = gr.Interface(fn=self.handle_inputs, 
                                      inputs=self.inputs, 
                                      outputs=self.outputs)
        
    def handle_inputs(self, file, periods):
        data = self.read_csv(file)
        self.train_model(data)
        forecast = self.predict(data, periods)
        fig = self.plot_graph(data, forecast)
        return fig
        
    def launch(self):
        self.interface.launch(share=False)