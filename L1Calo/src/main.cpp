#include <QApplication>
#include <QDialog>

#include "TileCIS/editscript.h"

int main(int argc, char *argv[])
{
  QApplication app(argc, argv);
  
  EditScript *dialog = new EditScript;
  dialog->show();
  return app.exec();
}
